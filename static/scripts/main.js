const btnLoadVideo = document.querySelector('.btn-load-video')
const loadVideoFile = document.querySelector('.upload-video-file')

const btnUploadVideo = document.querySelector('.btn-upload-video')
const allowed_exts = ['mp4', '3gp', 'wmv', 'avi']

const notification = document.querySelector('.notification')
const videoName = document.querySelector('.video-name')

const imageIndex = document.querySelector('.index-name')
const imageFrame = document.querySelector('.output-frame-image')

const searchQuery = document.querySelector('.txt-search-query')
const btnFindObject = document.querySelector('.btn-find')

btnFindObject.disabled = true
notification.style.display = 'none'
btnUploadVideo.disabled = true;
imageFrame.style.display = 'none'

searchQuery.onclick = ()=> btnFindObject.disabled = false

if(imageIndex.textContent !== ''){
    imageFrame.style.display = 'block'
    imageFrame.src = `static/resized_frames/${imageIndex.textContent}.jpeg` 
}

const showNotification = (notification_message) => {
    notification.style.display = 'flex'
    notification.textContent = notification_message;
    btnUploadVideo.disabled = true;
}

btnLoadVideo.addEventListener('click', ()=> {
    notification.style.display = 'none'
    btnUploadVideo.disabled = false;
    loadVideoFile.click()
})

loadVideoFile.onchange = ()=>{
    video = loadVideoFile.files[0]
    const video_name = video.name
    const video_size = video.size
    const video_type = video.type

    const ext = video_type.split('/')[1]
    const index = allowed_exts.findIndex(mime => mime === ext)

    if(video_type.split('/')[0] !== 'video'){
        showNotification("Videos only, upload a video.")
    }else if(index < 0){
        showNotification("Video extension not compatible.")
    }else if(video_size > 10000000){
        showNotification("Video size cannot exceed 10MB.")
    }else{
        videoName.textContent = `${video_name}`
        btnUploadVideo.disabled = false
    }
}