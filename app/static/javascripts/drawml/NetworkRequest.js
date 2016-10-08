function get_data() {
    $.ajax({
        url : 'http://localhost:5000/data/api',
        type : 'GET',
        async : true,
        success : function(dataList){
            console.log(dataList);
            //data_user_group
            //<div class="list-group-item data">나의 데이터 1</div>
              //       "user_id": 1,
              // "name": "file2",
              // "path": "file_path",
              // "date_modified": "2016-09-18 00:48:34",
              // "date_created": "2016-09-18 00:45:38",
              // "id": 7
            for(var x in dataList){
                $('#data_user_group').appendChild('<div class="list-group-item data">'+'dataList[x].name'+'</div>');
            }

        }
    });
}


//experiments/<exp_id>	GET	get specific exp
function get_data() {
    $.ajax({
        url : 'http://localhost:5000/data/api',
        type : 'GET',
        async : true,
        success : function(dataList){
            console.log(dataList);
        }
    });
}
//experiments/<exp_id>	PATCH	update exp
function get_data() {
    $.ajax({
        url : 'http://localhost:5000/data/api',
        type : 'GET',
        async : true,
        success : function(dataList){
            console.log(dataList);
        }
    });
}


//experiments/<exp_id>	DELETE	delete exp
function get_data() {
    $.ajax({
        url : 'http://localhost:5000/data/api',
        type : 'GET',
        async : true,
        success : function(dataList){
            console.log(dataList);
        }
    });
}

//experiments/<exp_id>stop	DELETE	stop exp
//experiments/<exp_id>status	GET	get experiement status