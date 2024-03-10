const getRequestOptions = {
    method: "GET",
    redirect: "follow"
}
//***API URLs ***/
const getPortsUrl = "/ports";
const connectSerialUrl = "/connect";
const sendCommandUrl = "/send";
const disconnectPortUrl = "/disconnect";
const getValuesUrl = "/getValues";
const rotateUrl = "/rotate";
const stopUrl = "/stop";

/*** Variable declarations ***/
let ports = [];
let selectedPort = "Select Input Port";
let isConnected = false;
let chartData = {}
var selectElement = document.getElementById("port-select");
let motorNumber = 0;
let keyPressed = false;
/*** API methods - START ***/
function getPorts() {
    ports = []
    fetch(getPortsUrl, getRequestOptions)
        .then((response) => response.text()).then((res) => {
            ports = JSON.parse(res).ports;
            console.log(ports);
            handleSelect();
        })
        .catch((error) => console.error(error));
}
function connectToPort(portName) {
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    const raw = JSON.stringify({
        "port": portName
    });

    const requestOptions = {
        method: "POST",
        headers: myHeaders,
        body: raw,
        redirect: "follow"
    };

    fetch(connectSerialUrl, requestOptions)
        .then((response) => response.text())
        .then((result) => {
            if (result) {
                var obj = JSON.parse(result)
                displayMessage(obj.message, '#198754');
            }
        })
        .catch((error) => {
            console.error(error);
            displayMessage("An error occurred. Please make sure port is not already in use", '#dc3545');
            setTimeout(() => { handleConnection() }, 2500)
        });
}
function disconnectPort() {
    fetch(disconnectPortUrl, getRequestOptions)
        .then((response) => response.text()).then((res) => {
            if (res) {
                var obj = JSON.parse(res);
                displayMessage(obj.message, 'red');
            }
        })
        .catch((error) => console.error(error));
}
function rotate(obj) {
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    const requestOptions = {
        method: "POST",
        headers: myHeaders,
        body: obj,
        redirect: "follow"
    };
    fetch(rotateUrl, requestOptions)
        .then((response) => response.text())
        .then((result) => {
            if (result) {
                var res = JSON.parse(result)
                displayMessage(res.message, '#198754');
            }
        })
        .catch((error) => {
            console.error(error);
            displayMessage("An error occurred. Please try again later.", '#dc3545');
        });
}
function stopMotor(motorId) {
    console.log("Stopping motor " + motorId);
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    const obj = JSON.stringify({ "motor_group": motorId })
    const requestOptions = {
        method: "POST",
        headers: myHeaders,
        body: obj,
        redirect: "follow"
    };
    fetch(stopUrl, requestOptions)
        .then((response) => response.text())
        .then((result) => {
            if (result) {
                var obj = JSON.parse(result)
                displayMessage(obj.message, '#198754');
            }
        })
        .catch((error) => {
            console.error(error);
            displayMessage("An error occurred.", '#dc3545');
            setTimeout(() => { handleConnection() }, 2500)
        });
}
function getValues() {
    fetch(getValuesUrl, getRequestOptions)
        .then((response) => response.text()).then((res) => {
            if (res) {
                console.log(res);
                var obj = JSON.parse(res);
                //displayMessage(obj.message, 'red');
                console.log(obj.message);
            }
        })
        .catch((error) => console.error(error));
}
/*** API methods - END ***/
/* Event Listeners */

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById("forwardButton").addEventListener('mousedown', () => {
        //Clicked forward
        rotateMotor('clockwise');
    })
    document.getElementById("forwardButton").addEventListener('mouseup', () => {
        //Released forward 
        if (motorNumber > 0)
            stopMotor(motorNumber);
    })
    document.getElementById("reverseButton").addEventListener('mousedown', () => {
        //Clicked reverse
        rotateMotor('anti-clockwise');
    })
    document.getElementById("reverseButton").addEventListener('mouseup', () => {
        //Released reverse 
        if (motorNumber > 0)
            stopMotor(motorNumber);
    })
})

/*** Functions - START ***/
function handleSelect() {
    if (selectElement) {
        if (ports.length > 0) {
            ports.forEach((port) => {
                var optionElement = document.createElement("option");
                optionElement.value = port;
                optionElement.text = port;
                selectElement.appendChild(optionElement);
            })
        }

    }
}
function portChanged($event) {
    selectedPort = $event.target.value;
}
function handleConnection() {
    let portButton = document.getElementById("port-btn")
    if (portButton.textContent === "Connect") {
        //Connecting
        if (selectedPort != "Select Input Port") {
            portButton.textContent = "Disconnect";
            portButton.classList.remove("btn-primary");
            portButton.classList.add("btn-danger");
            connectToPort(selectedPort);
        }
        else {
            displayMessage("Please select needed port", "red");
        }
    } else {
        //Disconnecting
        portButton.textContent = "Connect";
        portButton.classList.remove("btn-danger");
        portButton.classList.add("btn-primary");
        selectElement.selectedIndex = 0;
        selectedPort = selectElement.value;
        disconnectPort();
    }
}
function renderChart() {
    // Data for the chart
    chartData = {
        labels: Array.from({ length: 28 }, (_, i) => `m${i + 1}`),
        datasets: [{
            label: 'Motor Feedback',
            data: Array.from({ length: 28 }, () => Math.floor(Math.random() * 101)),
            backgroundColor: [
                'black',
            ]
        }]
    };

    // Configuration options
    const options = {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };
    // Destroy existing chart if it exists
    if (window.myChart instanceof Chart) {
        window.myChart.destroy();
    }
    // Get the context of the canvas element we want to select
    const ctx = document.getElementById('myChart').getContext('2d');

    // Create the chart
    window.myChart = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: options
    });
}
function updateChart() {
    if (chartData.datasets[0].data.length > 0)
        chartData.datasets.data = Array.from({ length: 28 }, () => Math.floor(Math.random() * 101)
        )
    var chart = document.getElementById('myChart');
    //console.log(chart.dataset[0].data[5]);
    //chart.update('none')
}
document.onkeydown = function (e) {
    switch (e.keyCode) {
        case 38:
            if (!keyPressed) {
                keyPressed = true
                rotateMotor('clockwise');
            }
            break;

        case 40:
            if (!keyPressed) {
                keyPressed = true;
                rotateMotor('anti-clockwise');
            }
            break;
    }
}
document.onkeyup = function (e) {
    if(keyPressed)
     keyPressed = !keyPressed;
    switch (e.keyCode) {
       case 38:
            if (motorNumber > 0)
                stopMotor(motorNumber);
            break;

        case 40:
            if (motorNumber > 0)
                stopMotor(motorNumber);
            break;
    }
}
function rotateMotor(direction) {
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    for (const radioButton of radioButtons) {
        if (radioButton.checked) {
            // Get the value of the selected radio button
            motorNumber = Number(radioButton.id);
            const sendObj = JSON.stringify({
                "direction": direction,
                "motor_group": motorNumber
            });
            console.log("Motor " + motorNumber + " rotated in " + direction);
            rotate(sendObj);
            //var displayString = "Motor "+motorId+" rotated in "+direction;
            //displayMessage(displayString, '#198754')
            return
        }
    }
}
function displayMessage(string, color) {
    var textDom = document.getElementById('display-text')
    textDom.innerHTML = string;
    textDom.style.color = color
    setTimeout(() => { textDom.innerHTML = '' }, 2500)
}
function init() {
    getPorts();
    renderChart();
    //setInterval(() => { getValues() }, 1000)
}
init();
/*** Functions - END ***/