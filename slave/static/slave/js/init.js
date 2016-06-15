
$(document).ready(function(){
    // the "href" attribute of .modal-trigger must specify the modal ID that wants to be triggered
    $('.modal-trigger').leanModal();
});

$('#modal1').openModal();


//初始化从机
function validate() {
    var ip = document.getElementById('set_ip').value;
    var port = document.getElementById('set_port').value;
    var room = document.getElementById('set_room_num').value;

    $.post("login",
    {
        'ip':ip,
        'port':port,
        'room_number':room
    },
        function(data){
            if (data == 1) {
                $('#modal1').closeModal();
                alert("成功连接中央空调！");
                return true;
            }
            else if (data == 0) {
                alert("连接失败！请重新输入IP/端口");
                return false;
            }
            else {
                alert("出错请重试！");
                return false;
            }
    });
    alert("主机未响应");
    return false;
}


var tempSlider = document.getElementById('temp_slider');

noUiSlider.create(tempSlider, {
	start: 25,
    step: 1,
	connect: 'lower',
	range: {
	  'min': 18,
	  'max': 25
	},
	format: {
	  to: function ( value ) {
		return value + '℃';
	  },
	  from: function ( value ) {
		return value.replace('℃', '');;
	  }
	}
});

var tempSliderValueElement = document.getElementById('set_temp');

tempSlider.noUiSlider.on('update', function( values, handle ) {
	tempSliderValueElement.innerHTML = values[handle];
});


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

var windSliderValueElement = document.getElementById('set_wind');
var windSliderValueElement2 = document.getElementById('set_wind_bottom');
var windVal;

windSlider.noUiSlider.on('update', function( values, handle ) {
    windVal = Math.round(values[handle]);
    switch(windVal)
    {
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
})


