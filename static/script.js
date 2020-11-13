var isAlarmEnabled = false;
var targetContainer = document.getElementById("barbora_count");
var eventSource = new EventSource("/stream")
var alarm_sound = new Audio('./static/service-bell_daniel_simion.mp3');

// Event source
eventSource.onopen = function (event) {
    console.log('Event source on open')
}

eventSource.onmessage = function (event) {
    console.log(event.data);
    updateLog(event.data);
    processStatus(event.data);
};

function updateLog(data) {
    targetContainer.innerHTML = '<img src="./static/barbora-veidas.jpg">' + data + '<br>' + targetContainer.innerHTML;
}

function processStatus(data) {
    if (isAlarmEnabled === false) {
        console.log("Not playing, Alarm disabled");
    } else if (data.includes(' 0 laisvų')) {
        console.log("0 laisvų");
    } else {
        alarm_sound.play();
        console.log("Played alarm");
    }
}

function toggleAlarm() {
    if (isAlarmEnabled === false) {
        isAlarmEnabled = true;
        console.log("Alarm enabled")
    } else {
        isAlarmEnabled = false;
        console.log("Alarm disabled")
    }
} 