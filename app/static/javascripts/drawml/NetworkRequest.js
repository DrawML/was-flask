
var server = "http://210.118.74.55:5000/"

function get_data() {
    $.ajax({
        url : server+'data/api',
        type : 'GET',
        async : false,
        success : function(dataList){
            var obj = JSON.parse(dataList);
           // console.log(obj);
            for(var x in obj){
                $('#data_user_group').append('<div class="list-group-item data ui-draggable ui-draggable-handle">'+obj[x].name+'</div>');
                var pushData = new Object();
                pushData.name=obj[x].name;
                pushData.id = obj[x].id;
                datalist.push(pushData);
            }
            $( init );
        }
    });
}

// /experiments/api/<exp_id>	GET	get specific exp
function get_exp() {
    $.ajax({
        url : server+'experiments/api/'+exp_id,
        type : 'GET',
        async : true,
        success : function(exp){
            console.log(exp);
            restoreModel(exp);
        }
    });
}

// /experiments/<exp_id>	PATCH	update exp
function update_exp(jsonInfo, callback) {
    $.ajax({
        url : server+'experiments/'+exp_id,
        type : 'PATCH',
        async : true,
        contentType : 'application/json',
        data : jsonInfo,
        dataType: 'json',
        xhr: function() {
            return window.XMLHttpRequest == null || new window.XMLHttpRequest().addEventListener == null
                ? new window.ActiveXObject("Microsoft.XMLHTTP")
                : $.ajaxSettings.xhr();
        },
        statusCode : {
            200: function (data, textStatus) {
                console.log(data);
                printResultMsg("Saved");
                !callback || callback();
            }
        }
    });
}

// /experiments/<exp_id>run	POST	run exp
function run_exp(xml) {
    $.ajax({
        url : server+'experiments/'+exp_id+'/run',
        type : 'POST',
        async : true,
        contentType : 'application/xml',
        data : xml,
        dataType : 'xml',
        statusCode : {
            200: function (data, textStatus) {
                console.log(data);
                console.log(textStatus);
                $('#footer-Stop-btn').show();
                get_expStatus();
                printResultMsg("Successfully request to run!");
                isProcessing = true;
            }
        }
    });
}


// /experiments/<exp_id>stop	DELETE	stop exp

//TODO : 작동이 안되는듯;;
function stop_exp() {
    $.ajax({
        url : server+'experiments/'+exp_id+'/stop',
        type : 'DELETE',
        async : true,
        statusCode : {
            200: function (data, textStatus) {
                console.log(data);
                console.log(textStatus);
                $('#footer-Stop-btn').hide();
                get_expStatus();
                printResultMsg("Successfully request to stop!");
            }
        }
    });
}


// /experiments/<exp_id>status	GET	get experiement status

function get_expStatus() {
    $.ajax({
        url : server+'experiments/'+exp_id+'/status',
        type : 'GET',
        async : true,
        success : function(result){
            console.log(result);

            if(result == 'success'){
                $('#footer-status').html('<span class="label label-success" style="font-size:14px;">' + result + '</span>');
                $('#footer-Stop-btn').hide();
            }else if(result == 'fail'){
                $('#footer-status').html('<span class="label label-important" style="font-size:14px;">' + result + '</span>');
                $('#footer-Stop-btn').hide();
            }else if(result == 'cancel'){
                $('#footer-status').html('<span class="label label-warning" style="font-size:14px;">' + result + '</span>');
                $('#footer-Stop-btn').hide();
            }else if(result == 'running'){
                $('#footer-status').html('<span class="label label-inverse" style="font-size:14px;">' + result + '</span>');
                $('#footer-Stop-btn').show();
            }else if(result == 'idle'){
                $('#footer-status').html('<span class="label label-idle" style="font-size:14px;">' + result + '</span>');
                $('#footer-Stop-btn').hide();
            }else{
                //Status Error
                alert('Can not Match Status');
            }
        }
    });
}

