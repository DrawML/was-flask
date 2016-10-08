
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
            restoreModel(exp);
        }
    });
}

// /experiments/<exp_id>	PATCH	update exp
function update_exp(jsonInfo) {
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
        success : function(){
             $('#footer-Stop-btn').show();
            isProcessing=true;
        }
    });
}


// /experiments/<exp_id>stop	DELETE	stop exp

function stop_exp() {
    $.ajax({
        url : server+'experiments/'+exp_id+'/stop',
        type : 'DELETE',
        async : true,
        success : function(){
            $('#footer-Stop-btn').hide();
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
                $('#footer-Stop-btn').hide();
            }else if(result == 'fail'){
                $('#footer-Stop-btn').hide();
            }else if(result == 'cancel'){
                $('#footer-Stop-btn').hide();
            }else if(result == 'running'){
                $('#footer-Stop-btn').show();
            }else if(result == 'No status'){
                $('#footer-Stop-btn').hide();
            }else{
                //Status Error
                alert('Can not Match Status');
            }
        }
    });
}

