
var server = "http://210.118.74.55:5000"

function get_data() {
    $.ajax({
        url : server+'/data/api',
        type : 'GET',
        async : true,
        success : function(dataList){
            //console.log(dataList);
            for(var x in dataList){
                $('#data_user_group').append('<div class="list-group-item data ui-draggable ui-draggable-handle">'+'dataList[x].name'+'</div>');
            }
            $( init );
        }
    });
}
