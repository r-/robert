function UpdateCameraFeed(){
    fetch('/camera/video_feed', { method: 'HEAD' })
        .then(response => {
            if (response.ok) {
                // Camera is available, show the video feed
                document.getElementById('videoFeed').style.display = 'block';
                document.getElementById('noCameraMessage').style.display = 'none';
            } else {
                // Camera is not available, show the no camera message
                document.getElementById('videoFeed').style.display = 'none';
                document.getElementById('noCameraMessage').style.display = 'block';
            }
        })
        .catch(() => {
            document.getElementById('videoFeed').style.display = 'none';
            document.getElementById('noCameraMessage').style.display = 'block';
        });
};
setInterval(UpdateCameraFeed, 2000)