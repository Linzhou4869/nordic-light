'===============================================================================
' Nordic Light Gallery - Master Display Player
' Device: BrightSign XD133 (Main Lobby)
' Role: Master node for synchronized playback with corridor display
'===============================================================================

function main()
    ' Initialize display
    display = CreateObject("roDisplay")
    display.SetMode("1920x1080p60")
    
    ' Load sync configuration
    config = LoadConfig("master_config.json")
    
    ' Initialize network sync
    syncManager = CreateObject("roSyncManager")
    syncManager.SetMasterMode(true)
    syncManager.SetSyncInterval(config.SyncIntervalMs)
    syncManager.EnableFrameLock(true)
    
    ' Load playlist
    playlist = CreateObject("roPlaylist")
    for each videoFile in config.Playlist
        playlist.AddVideo(videoFile)
    next
    
    ' Main playback loop
    while true
        ' Sync point - wait for frame lock
        syncManager.WaitForSync()
        
        ' Play current video
        videoPlayer = CreateObject("roVideoPlayer")
        videoPlayer.SetLoopMode(false)
        videoPlayer.Play(playlist.GetCurrent())
        
        ' Send sync pulse to slaves
        syncManager.BroadcastSync()
        
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
    wend
end function

function LoadConfig(filename as string) as dynamic
    configFile = CreateObject("roFileSystem")
    configData = configFile.ReadFile(filename)
    return ParseJson(configData)
end function
