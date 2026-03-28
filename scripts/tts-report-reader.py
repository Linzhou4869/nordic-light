#!/usr/bin/env python3
"""
Text-to-Speech Report Reader
Converts weekly build reports to speech using Edge TTS and plays through speakers.
"""

import os
import re
import json
import asyncio
from datetime import datetime
from pathlib import Path

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("WARNING: edge-tts not available")

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
WORKSPACE = SCRIPT_DIR.parent  # Go up one level from scripts/ to workspace
REPORTS_DIR = WORKSPACE / "reports"
AUDIO_DIR = WORKSPACE / "audio"

# Ensure directories exist
AUDIO_DIR.mkdir(exist_ok=True)
SCRIPT_DIR.mkdir(exist_ok=True)


def extract_report_data(report_path):
    """Extract key metrics from the markdown report."""
    data = {
        "period": "",
        "generated": "",
        "total_builds": 0,
        "success_rate": 0.0,
        "avg_duration": 0,
        "failures": 0,
        "compilation_errors": 0,
        "test_failures": 0,
        "dependency_issues": 0,
        "timeout_errors": 0,
        "build_api_p95": 0,
        "cpu_avg": "0",
        "memory_avg": "0"
    }
    
    try:
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Extract period
        period_match = re.search(r'Report Period:\s*(\d{4}-\d{2}-\d{2})\s*to\s*(\d{4}-\d{2}-\d{2})', content)
        if period_match:
            data["period"] = f"{period_match.group(1)} to {period_match.group(2)}"
        
        # Extract generated date
        gen_match = re.search(r'Generated:\s*(.+?)(?:\n|$)', content)
        if gen_match:
            data["generated"] = gen_match.group(1).strip()
        
        # Extract from markdown tables (more reliable than JSON)
        # Total Builds from table
        total_match = re.search(r'\|\s*Total Builds\s*\|\s*(\d+)', content)
        if total_match:
            data["total_builds"] = int(total_match.group(1))
        
        # Avg Build Duration from table
        duration_match = re.search(r'\|\s*Avg Build Duration\s*\|\s*(\d+)', content)
        if duration_match:
            data["avg_duration"] = int(duration_match.group(1))
        
        # Build Failures from table
        failures_match = re.search(r'\|\s*Build Failures\s*\|\s*(\d+)', content)
        if failures_match:
            data["failures"] = int(failures_match.group(1))
        
        # Extract failure breakdown from table
        failure_table = re.search(r'Failure Type.*?\|.*?Compilation Errors.*?\|\s*(\d+).*?\|\s*(\d+).*?\|\s*(\d+).*?\|\s*(\d+)', content, re.DOTALL)
        if failure_table:
            data["compilation_errors"] = int(failure_table.group(1))
            data["test_failures"] = int(failure_table.group(2))
            data["dependency_issues"] = int(failure_table.group(3))
            data["timeout_errors"] = int(failure_table.group(4))
        
        # Extract latency from JSON or text
        latency_match = re.search(r'"build_api_p95_ms":\s*(\d+)', content)
        if latency_match:
            data["build_api_p95"] = int(latency_match.group(1))
        
        # Extract infrastructure from table
        infra_match = re.search(r'\|\s*CPU Utilization\s*\|\s*(\d+)%', content)
        if infra_match:
            data["cpu_avg"] = infra_match.group(1)
        
        mem_match = re.search(r'\|\s*Memory Utilization\s*\|\s*(\d+)%', content)
        if mem_match:
            data["memory_avg"] = mem_match.group(1)
        
        # Calculate success rate
        if data["total_builds"] > 0:
            successful = data["total_builds"] - data["failures"]
            data["success_rate"] = round((successful / data["total_builds"]) * 100, 1)
        
    except Exception as e:
        print(f"Error parsing report: {e}")
    
    return data


def generate_speech_script(data):
    """Generate a natural-sounding speech script from report data."""
    
    # Calculate success status
    success_status = "healthy" if data["success_rate"] >= 95 else "needs attention"
    latency_status = "normal" if data["build_api_p95"] < 1000 else "elevated"
    
    script = f"""Good morning. This is your weekly build metrics report for the Spring PetClinic microservice.

Report period: {data["period"]}.
Generated on {data["generated"]}.

Here are this week's key metrics:

Total builds executed: {data["total_builds"]}.
Build success rate: {data["success_rate"]} percent.
Average build duration: {data["avg_duration"]} seconds.
Total build failures: {data["failures"]}.

The build health status is {success_status}.

Breaking down the failures:
{data["compilation_errors"]} compilation errors.
{data["test_failures"]} test failures.
{data["dependency_issues"]} dependency issues.
{data["timeout_errors"]} timeout errors.

Performance metrics:
Build API P95 latency: {data["build_api_p95"]} milliseconds, which is {latency_status}.

Infrastructure utilization:
Average CPU usage: {data["cpu_avg"]} percent.
Average memory usage: {data["memory_avg"]} percent.

Recommendations:
"""
    
    # Add dynamic recommendations
    recommendations = []
    if data["success_rate"] < 95:
        recommendations.append("Review recent commits and test failures to improve build stability.")
    if data["build_api_p95"] > 1000:
        recommendations.append("Consider optimizing build cache to reduce latency.")
    if int(data["cpu_avg"] or 0) > 70:
        recommendations.append("CPU utilization is high. Consider scaling build infrastructure.")
    if int(data["memory_avg"] or 0) > 70:
        recommendations.append("Memory utilization is elevated. Review build process memory allocation.")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            script += f"{i}. {rec}\n"
    else:
        script += "All metrics are within acceptable thresholds. No immediate action required.\n"
    
    script += """
This concludes the weekly build report.
Thank you for listening."""
    
    return script


async def generate_audio_edge_tts(text, output_path, voice="en-US-AriaNeural", rate="+0%"):
    """Generate audio using Edge TTS (Microsoft's cloud TTS)."""
    
    if not EDGE_TTS_AVAILABLE:
        print("ERROR: edge-tts not available")
        return False
    
    try:
        communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
        await communicate.save(str(output_path))
        print(f"Audio saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error generating speech with Edge TTS: {e}")
        return False


def play_audio(audio_path):
    """Play audio file through system speakers."""
    
    # Try different playback methods
    playback_commands = [
        f"aplay {audio_path}",  # ALSA
        f"paplay {audio_path}",  # PulseAudio
        f"ffplay -nodisp -autoexit {audio_path} 2>/dev/null",  # FFmpeg
        f"mpg123 {audio_path} 2>/dev/null",  # mpg123
        f"cvlc --play-and-exit {audio_path} 2>/dev/null",  # VLC
    ]
    
    for cmd in playback_commands:
        try:
            result = os.system(f"{cmd} 2>/dev/null")
            if result == 0:
                print(f"Audio playing through: {cmd.split()[0]}")
                return True
        except:
            continue
    
    print("WARNING: Could not play audio - no suitable audio player found")
    print(f"Audio file saved but not played: {audio_path}")
    return False


async def main_async():
    """Async main entry point."""
    
    print("=" * 60)
    print("Weekly Build Report - Text-to-Speech Converter")
    print("=" * 60)
    
    # Find the latest report
    report_files = list(REPORTS_DIR.glob("weekly-build-report-*.md"))
    if not report_files:
        print("ERROR: No report files found in reports/")
        return 1
    
    latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
    print(f"Found report: {latest_report.name}")
    
    # Extract data from report
    print("Extracting metrics from report...")
    data = extract_report_data(latest_report)
    
    # Generate speech script
    print("Generating speech script...")
    script = generate_speech_script(data)
    
    # Save the script
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    script_path = SCRIPT_DIR / f"speech-script-{timestamp}.txt"
    with open(script_path, 'w') as f:
        f.write(script)
    print(f"Speech script saved to: {script_path}")
    
    # Generate audio using Edge TTS
    audio_path = AUDIO_DIR / f"weekly-report-{timestamp}.mp3"
    
    if EDGE_TTS_AVAILABLE:
        print("Generating audio with Edge TTS (Microsoft Azure voices)...")
        
        # Use a professional, clear voice
        voice = "en-US-AriaNeural"  # Professional female voice
        rate = "-10%"  # Slightly slower for clarity
        
        success = await generate_audio_edge_tts(script, audio_path, voice, rate)
        
        if success:
            file_size = audio_path.stat().st_size / 1024
            print(f"\nAudio file created: {audio_path}")
            print(f"File size: {file_size:.1f} KB")
            
            # Play the audio
            print("\nPlaying audio through speakers...")
            play_audio(audio_path)
        else:
            print("Audio generation failed, but script was saved.")
    else:
        print("Edge TTS not available - speech script saved only.")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Report: {latest_report.name}")
    print(f"  Script: {script_path.name}")
    if EDGE_TTS_AVAILABLE:
        print(f"  Audio: {audio_path.name}")
    print("=" * 60)
    
    return 0


def main():
    """Sync wrapper for async main."""
    return asyncio.run(main_async())


if __name__ == "__main__":
    exit(main())
