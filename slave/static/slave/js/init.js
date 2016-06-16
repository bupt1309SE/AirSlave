$(document).ready(function () {
    // the "href" attribute of .modal-trigger must specify the modal ID that wants to be triggered
    $('.modal-trigger').leanModal();
    $('#modal1').openModal();
});

var mainLoopTimer;
var subLoopTimer;

/* 初始化从机 */
function validate() {
    var ip = document.getElementById('set_ip').value;
    var port = document.getElementById('set_port').value;
    var room = document.getElementById('set_room_num').value;

    $.post("login",
        {
            'ip': ip,
            'port': port,
            'room_number': room
        },
        function (data) {
            if (data == 1) {
                $('#modal1').closeModal();
                Materialize.toast("成功连接中央空调！",4000);
                document.getElementById('show_room_num').innerHTML = room;
                mainLoopTimer = setTimeout('mainLoop()', 1000);
                return true;
            }
            else if (data == 0) {
                alert("连接失败！请重新输入IP/端口/房间号");
                return false;
            }
            else {
                alert("出错请重试！");
                return false;
            }
        });
    //alert("主机未响应");
    return false;
}

var workModeElement = document.getElementById('show_work_mode');
var workModeElemEN = document.getElementById('show_work_mode_en');
var roomTempElement = document.getElementById('show_room_temp');
var windElement = document.getElementById('show_wind');
var windElementEN = document.getElementById('show_wind_bottom');
var totalCostElement = document.getElementById('show_cost');
var powerConsumeElement = document.getElementById('show_power');
var powerPriceElement = document.getElementById('show_price');

/* 循环更新 */
function mainLoop() {
    $.get("get_info",
        function (data) {
            if (data.is_log == "True" && data.is_conn == "False") {
                Materialize.toast("与主机连接断开,尝试重连……", 4000);
                subLoopTimer = setTimeout('subLoop()', 4000);
            }
            else if (data.is_log == "True" && data.is_conn == "True") {
                //Materialize.toast("get info succeed", 1000);
                //Materialize.toast(data.current_speed, 1000);
                updateUI(data);

                mainLoopTimer = setTimeout('mainLoop()', 1000);
            }
        }
    );
}

/* 循环重连 */
function subLoop() {
    Materialize.toast("尝试重连……", 4000);
    $.get("get_info",
        function (data) {
            if (data.is_conn == "True") {
                Materialize.toast("已与服务器重连", 4000);
                //mainLoopTimer = setTimeout('mainLoop()', 1000);
                mainLoopTimer = setTimeout('validate()', 1000);
                setTimeout('resendRequest()', 3000);
            }
            else {
                Materialize.toast("重连失败，5秒后重试", 4000);
                subLoopTimer = setTimeout('subLoop()', 5000);
            }
        }
    );
}

/* 重发请求 */
function resendRequest() {
    $.post("target_reply",
        {
            'target_temp': tempSlider.noUiSlider.get()
        }
    );
    $.post("speed_reply",
        {
            'speed_choice': windArray[Math.round(windSlider.noUiSlider.get())]
        }
    );
}

/* update UI */
function updateUI(data) {
    if (data.mode == "hot") {
        workModeElement.innerHTML = "制热";
        workModeElemEN.innerHTML = "HOT";
        updateTempSlider("hot");
    }
    else if (data.mode == "cold") {
        workModeElement.innerHTML = "制冷";
        workModeElemEN.innerHTML = "COOL";
        updateTempSlider("cool");
    }

    roomTempElement.innerHTML = data.current_temp.toFixed(2) + "℃";

    if (data.current_speed == "standby") {
        windElement.innerHTML = "待机";
        windElementEN.innerHTML = "STOP";
    }
    else if (data.current_speed == "low") {
        windElement.innerHTML = "低风";
        windElementEN.innerHTML = "LOW";
    }
    else if (data.current_speed == "medium") {
        windElement.innerHTML = "中风";
        windElementEN.innerHTML = "MED";
    }
    else if (data.current_speed == "high") {
        windElement.innerHTML = "高风";
        windElementEN.innerHTML = "HIGH";
    }

    totalCostElement.innerHTML = data.total_cost.toFixed(2) + "$";
    powerConsumeElement.innerHTML = data.power_consump.toFixed(2);
    powerPriceElement.innerHTML = data.power_price.toFixed(2);
}

/* 设置温度滑块 */
var tempSlider = document.getElementById('temp_slider');

noUiSlider.create(tempSlider, {
        start: 25,
        step: 1,
        connect: 'lower',
        range: {
            'min': 18,
            'max': 25
        }
    }
);

function updateTempSlider(type) {
    var min, max, conn;
    if (type == "hot") {
        min = 25;
        max = 30;
        conn = 'lower';
    }
    else {  //type == "cool"
        min = 18;
        max = 25;
        conn = 'upper';
    }
    tempSlider.noUiSlider.updateOptions({
        connect: conn,
        range: {
            'min': min,
            'max': max
        }
    });
}


/* 更新设置温度元素 */
var tempSliderValueElement = document.getElementById('set_temp');

tempSlider.noUiSlider.on('update', function (values, handle) {
    tempSliderValueElement.innerHTML = Math.round(values[handle]) + '℃';
});

tempSlider.noUiSlider.on('change', function () {
    $.post("target_reply",
        {
            'target_temp': tempSlider.noUiSlider.get()
        }
    );
});

/* 设置风速滑块 */
var windSlider = document.getElementById('wind_slider');

noUiSlider.create(windSlider, {
    start: 0,
    step: 1,
    connect: 'lower',
    range: {
        min: 0,
        max: 3
    }
});

/* 更新设置风速元素 */
var windVal;
var windSliderValueElement = document.getElementById('set_wind');
var windSliderValueElement2 = document.getElementById('set_wind_bottom');

windSlider.noUiSlider.on('update', function (values, handle) {
    windVal = Math.round(values[handle]);
    switch (windVal) {
        case 0:
            windSliderValueElement.innerHTML = '待机';
            windSliderValueElement2.innerHTML = 'STOP';
            break;
        case 1:
            windSliderValueElement.innerHTML = '低风';
            windSliderValueElement2.innerHTML = 'LOW';
            break;
        case 2:
            windSliderValueElement.innerHTML = '中风';
            windSliderValueElement2.innerHTML = 'MED';
            break;
        case 3:
            windSliderValueElement.innerHTML = '高风';
            windSliderValueElement2.innerHTML = 'HIGH';
            break;
    }
});

var windArray = ["standby", "low", "medium", "high"];

windSlider.noUiSlider.on('change', function () {
    $.post("speed_reply",
        {
            'speed_choice': windArray[Math.round(windSlider.noUiSlider.get())]
        }
    );
});

$('#logout').click(function logOut() {
    $.get("logout",
        function (data) {
            if (data == 1)
                Materialize.toast("注销成功", 5000);
            else
                alert("注销失败");
        }
    );

});


