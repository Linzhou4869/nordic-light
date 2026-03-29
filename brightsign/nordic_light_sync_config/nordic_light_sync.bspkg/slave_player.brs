'===============================================================================
' Nordic Light Gallery - Slave Display Player
' Device: BrightSign HD102 (Secondary Corridor)
' Role: Slave node - mirrors master (lobby) display with frame-locked sync
'===============================================================================

function main()
    ' Initialize display
    display = CreateObject("roDisplay")
    display.SetMode("1080x1920p60")  ' Portrait mode for corridor
    
    ' Load sync configuration
    config = LoadConfig("slave_config.json")
    
    ' Initialize network sync
    syncManager = CreateObject("roSyncManager")
    syncManager.SetMasterMode(false)
    syncManager.SetMasterAddress(config.MasterIPAddress)
    syncManager.EnableFrameLock(true)
    syncManager.SetSyncTimeout(5000)  ' 5 second timeout
    
    ' Load playlist (same as master)
    playlist = CreateObject("roPlaylist")
    for each videoFile in config.Playlist
        playlist.AddVideo(videoFile)
    next
    
    ' Wait for master sync signal
    print "Waiting for master sync signal..."
    syncManager.WaitForMasterSync()
    print "Sync established with master"
    
    ' Main playback loop - mirrors master
    while true
        ' Wait for sync pulse from master
        syncEvent = syncManager.WaitForSyncPulse()
        
        if syncEvent.IsValid()
            ' Play current video in sync with master
            videoPlayer = CreateObject("roVideoPlayer")
            videoPlayer.SetLoopMode(false)
            videoPlayer.Play(playlist.GetCurrent())
            
            ' Handle events
            while videoPlayer.IsPlaying()
                event = wait(0, videoPlayer.GetMessagePort())
                if type(event) = "roVideoPlayerEvent"
                    if event.IsPlaybackComplete()
                        exit while
                    end if
                end if
            wend
            
            ' Move to next video
            playlist.Next()
            if playlist.IsAtEnd()
                playlist.Rewind()
            end if
        else
            ' Lost sync - attempt reconnection
            print "Sync lost, attempting reconnection..."
            syncManager.ReconnectToMaster()
        end if
    wend
end function

function LoadConfig(filename as string) as dynamic
    configFile = CreateObject("roFileSystem")
    configData = configFile.ReadFile(filename)
    return ParseJson(configData)
end function
