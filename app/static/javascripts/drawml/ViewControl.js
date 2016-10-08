var datalist =[];

function getDataIDByName(name){
    var result ="";
    for(var x =0 ; x<datalist.length;x++)
    {
        if(datalist[x].name==name){
            result=datalist[x].id;
            break;
        }
    }
    return result;
}

function getDataNameById(id){
    var result ="";
    for(var x =0 ; x<datalist.length;x++)
    {
        if(datalist[x].name==id){
            result=datalist[x].name;
            break;
        }
    }
    return result;
}

/////////////////////////////////////////////
////////////Drag & Drop Event Handler////////
/////////////////////////////////////////////
$( init );
function myHelper(event) {
    var iid= $(this).text();
    if($(this).hasClass('dataPreprocess') || $(this).hasClass('data')){
        return '<div id="dataDraggableHelper">'+
            '<h3 style="display: table-cell;vertical-align: middle;text-align: center;">'+iid+'</h3>'+
            '</div>';
    }
    return '<div id="draggableHelper">'+
        '<h3 style="display: table-cell;vertical-align: middle;text-align: center">'+iid+'</h3>'+
        '</div>';
}

//Check ML Model
function canMLmodel(){
    for(var x =0; x<models.length;x++){
        if(models[x] instanceof InputModel || models[x] instanceof DataPreprocessingModel){
            continue;
        }else{
            return false;
        }
    }
    return true;
}

function handleDragStop(event,ui){
    console.log($(this).attr('id'));
}


function handleDropEvent( event, ui ) {
    var draggable = ui.draggable;
    var wi=$('#leftSideBar').width();
    var ContainerTop =$('#paintContainer').offset().top;
    if(ui.draggable.attr('id')=="LinearRegression"){
        if(!canMLmodel()) {
            alert("Already have ML model...!");
            return;
        }
        clearDataShapeOption();
        clearLayerOption();
        makeDefaultOptions()
            var l = new Regression(modelCnt++,'linear_regression',canvasX-wi-150,canvasY-ContainerTop);
            models.push(l);
            currentSelectedModel=l;
            canvas.add(l.fabricModel);
            canvas.renderAll();
    }else if(ui.draggable.attr('id')=="PolynomialRegression"){
        if(!canMLmodel()) {
            alert("Already have ML model...!");
            return;
        }
        clearDataShapeOption();
        clearLayerOption();
        makeDefaultOptions()
        var l = new Regression(modelCnt++,'Polynomial regression',canvasX-wi-150,canvasY-ContainerTop);
        models.push(l);
        currentSelectedModel=l;
        canvas.add(l.fabricModel);
        canvas.renderAll();
    }else if(ui.draggable.attr('id')=="SoftMaxRegression"){
        if(!canMLmodel()) {
            alert("Already have ML model...!");
            return;
        }
        clearDataShapeOption();
        clearLayerOption();
        makeDefaultOptions()
        var l = new Regression(modelCnt++,'softmax_regression',canvasX-wi-150,canvasY-ContainerTop);
        models.push(l);
        currentSelectedModel=l;
        canvas.add(l.fabricModel);
        canvas.renderAll();
    }else if(ui.draggable.attr('id')=="NeuralNetworks"){
        if(!canMLmodel()) {
            alert("Already have ML model...!");
            return;
        }
        clearLayerOption();
        clearDataShapeOption();
        makeDefaultOptions()
        var l = new NeuralNetworks(modelCnt++,canvasX-wi-150,canvasY-ContainerTop);
        models.push(l);
        currentSelectedModel=l;
        canvas.add(l.fabricModel);
        l.updateFabricModel();
        canvas.renderAll();
        makeLayerOption(1);
        $('#model-addlayer-btn').show();
    }else if(ui.draggable.attr('id')=="ConvolutionNeuralNet"){
        if(!canMLmodel()) {
            alert("Already have ML model...!");
            return;
        }
        clearLayerOption();
        clearDataShapeOption();
        makeDefaultOptions()
        var l = new ConvolutionNeuralNetworks(modelCnt++,canvasX-wi-150,canvasY-ContainerTop);
        models.push(l);
        currentSelectedModel=l;
        canvas.add(l.fabricModel);
        l.updateFabricModel();
        canvas.renderAll();
        makeCNNLayerOption(1);
        $('#model-addlayer-btn').show();
    }else if(ui.draggable.hasClass('dataPreprocess')){
        clearLayerOption();
        clearDataShapeOption();
        clearDefaultOptions();
        var fileName = ui.draggable.text();
        var l = new DataPreprocessingModel(modelCnt++,fileName,canvasX-wi-150,canvasY-ContainerTop);
        models.push(l);
        currentSelectedModel=l;
        canvas.add(l.fabricModel);
        canvas.renderAll();
    }else if(ui.draggable.hasClass('data')){
        clearLayerOption();
        makeDataShapeOption();
        clearDefaultOptions();
        var fileName = ui.draggable.text();
        var l = new InputModel(modelCnt++,fileName,getDataIDByName(fileName),canvasX-wi-150,canvasY-ContainerTop);
        models.push(l);
        currentSelectedModel=l;
        canvas.add(l.fabricModel);
        canvas.renderAll();
    }
}


function init() {
    $('#leftSideBar .list-group-item').draggable( {
        cursor: 'move',
        containment: 'document',
        helper: myHelper,
        stop: handleDragStop
    } );
    $('#canvasContaianer').droppable( {
        drop: handleDropEvent
    } );
}

/////////////////////////////////////////////
////////Control HTML&CSS Using JQuery////////
/////////////////////////////////////////////

$(document).ready(function(){

    get_exp();
    get_expStatus();
    get_data();

    clearDefaultOptions();
    clearDataShapeOption();
    clearConnectModelDelete();
    $('#footer-Stop-btn').hide();


    //왼쪽 탭 설정
    $('#model_group').show();
    $('#data_preprocessing_group').hide();
    $('#data_user_group').hide();

    $('#model_select_view').click(function(){
        if($(this).hasClass(".active")===true) return;
        else {
            $(this).addClass("active");
            $('#data_select_view').removeClass("active");
0
            $('#model_group').show();
            $('#data_preprocessing_group').hide();
            $('#data_user_group').hide();
        }
    });

    $('#data_select_view').click(function(){
        if($(this).hasClass(".active")===true) return;
        else {
            $(this).addClass("active");
            $('#model_select_view').removeClass("active");

            $('#model_group').hide();
            $('#data_preprocessing_group').show();
            $('#data_user_group').show();
        }
    });



    $('#model-addlayer-btn').hide();

    //Change Initializer
    $('#change-Initializer-random_normal').click(function(){
        $('#change-Initializer-current').text($(this).text());
        $('#change-Initializer-value').show();
        $('#change-Initializer-value').val(currentSelectedModel.initializer.val);
        $('#change-Initializer-value-max').hide();
        $('#change-Initializer-value-min').hide();
        currentSelectedModel.changeInitializer($(this).text());

    });
    $('#change-Initializer-random_uniform').click(function(){
        $('#change-Initializer-current').text($(this).text());
        $('#change-Initializer-value').hide();
        $('#change-Initializer-value-max').show();
        $('#change-Initializer-value-min').show();
        $('#change-Initializer-value-max').val(currentSelectedModel.initializer.max);
        $('#change-Initializer-value-min').val(currentSelectedModel.initializer.min);
        currentSelectedModel.changeInitializer($(this).text());
    });

    $('#change-Initializer-value-input').on("change paste keyup", function() {
        currentSelectedModel.initializer.val = $(this).val();
    });

    $('#change-Initializer-value-max-input').on("change paste keyup", function() {
        currentSelectedModel.initializer.max = $(this).val();
    });

    $('#change-Initializer-value-min-input').on("change paste keyup", function() {
        currentSelectedModel.initializer.min = $(this).val();
    });


    //TODO : ?????????????????????이게뭐
    //Change Optimizer
    $('#change-Optimizer-gradientDescent').click(function(){
        $('#change-Optimizer-current').text($(this).text());
        currentSelectedModel.changeOptimizer($(this).text());
    });
    $('#change-Optimizer-adadelta').click(function(){
        $('#change-Optimizer-current').text($(this).text());
        currentSelectedModel.changeOptimizer($(this).text());
    });
    $('#change-Optimizer-adagrad').click(function(){
        $('#change-Optimizer-current').text($(this).text());
        currentSelectedModel.changeOptimizer($(this).text());
    });
    $('#change-Optimizer-momentum').click(function(){
        $('#change-Optimizer-current').text($(this).text());
        currentSelectedModel.changeOptimizer($(this).text());
    });
    $('#change-Optimizer-adam').click(function(){
        $('#change-Optimizer-current').text($(this).text());
        currentSelectedModel.changeOptimizer($(this).text());
    });
    $('#change-Optimizer-ftrl').click(function(){
        $('#change-Optimizer-current').text($(this).text());
        currentSelectedModel.changeOptimizer($(this).text());
    });
    $('#change-Optimizer-rmsprop').click(function(){
        $('#change-Optimizer-current').text($(this).text());
        currentSelectedModel.changeOptimizer($(this).text());
    });

    $('#change-Optimizer-learningRate-input').on("change paste keyup", function() {
        currentSelectedModel.optimizer.learningRate = $(this).val();
    });

    //Change Regularization
    $('#change-regularization-enable-false').click(function(){
        $('#change-regularization-current').text($(this).text());
        $('#change-regularization-lambda').hide();
        currentSelectedModel.setRegularizationEnable('false');
    });
    $('#change-regularization-enable-true').click(function(){
        $('#change-regularization-current').text($(this).text());
        $('#change-regularization-lambda').show();
        $('#change-regularization-lambda-input').val(currentSelectedModel.lambda);
        currentSelectedModel.setRegularizationEnable('true');
    });
    $('#change-regularization-lambda-input').on("change paste keyup", function() {
        currentSelectedModel.setLambda($(this).val());
    });

    //Change Training Epoch
    $('#change-trainingEpoch-input').on("change paste keyup", function() {
        currentSelectedModel.changeTrainingEpoch($(this).val());
    });


    var isProcessing = false;

    //Models To XML
    $('#footer-toxml-btn').click(function () {
        if(isProcessing) return;

        var exp_xml=makeXML();
        var model_xml=makeModelXML();


        var exp_data=new Object();
        exp_data.drawing = model_xml;
        exp_data.xml = exp_xml;
        var x = new Object();
        x.exp_data=exp_data;
        var jsonInfo = JSON.stringify(x);

        console.log(jsonInfo);

        update_exp(jsonInfo);
        run_exp(exp_xml);

    });

    $('#footer-Stop-btn').click(function () {
        isProcessing=false;
        stop_exp();

        $(this).hide();
    });


    //Connection Delete

    $('#connectionDelete').click(function () {
        deleteLineArrow();
    });

    //Model delete
    $('#model-delete-btn').click(function () {
        clearLayerOption();
        clearLine(currentSelectedModel);
        var curIdx=getModelIdxById(currentSelectedModel.ID);
        models.splice(curIdx,1);
        canvas.remove(currentSelectedModel.fabricModel);
        currentSelectedModel=null;
    });

    $('#model-addlayer-btn').click(function(){
        if((currentSelectedModel instanceof NeuralNetworks)) {
            //Option UI 생성
            makeLayerOption(currentSelectedModel.getLayerLength() + 1);
            //모델객체에 레이어 추가.
            currentSelectedModel.addLayerBackOf(currentSelectedModel.getLayerLength() - 1);
        }else if(currentSelectedModel instanceof ConvolutionNeuralNetworks){
            makeCNNLayerOption(currentSelectedModel.getLayerLength()+1);
            currentSelectedModel.addLayerBackOf(currentSelectedModel.getLayerLength() - 1);
        }
    });


    //Data INPUT EVENT

    $('#change-datashape-x-input').on("change paste keyup", function() {
        currentSelectedModel.changeShapeX($(this).val());
    });
    $('#change-datashape-y-input').on("change paste keyup", function() {
        currentSelectedModel.changeSHapeY($(this).val());
    });


    //Model Selection

    $('#connectModel').click(function () {
        if($(this).hasClass('btn-success')){//선택했을때
            connectStart();
        }else{//선택중일때 -> 취소
            connectComplete();
        }
    });

});

/////////////////////////////////////////////
////////////Control Connect Model////////////
/////////////////////////////////////////////

function connectStart(){
    $('#connectModel').removeClass('btn-success');
    $('#connectModel').addClass('btn-danger');
    $('#connectModel').text("Connecting.....");
    canvas.deactivateAll().renderAll();
    makingModel=true;

}

function connectComplete(){
    $('#connectModel').removeClass('btn-danger');
    $('#connectModel').addClass('btn-success');
    $('#connectModel').text("Connect Model");
}


/////////////////////////////////////////////
////////////////XML Functions////////////////
/////////////////////////////////////////////


//INPUT XML
//DATA_PROCESSING XML
function makeXML() {
    var XML = new XMLWriter();
    XML.BeginNode("experiment");

    var visit = new Array();
    for(var x =0; x<models.length;x++) visit.push(false);
    var inputList = [];

    //Input
    for(var x=0 ; x<models.length;x++){
        if(models[x] instanceof InputModel) {
            inputList.push(models[x]);
            visit[x]=true;
        }
    }
    if(inputList.length ==0) {
        alert("No input Data");
        return ;
    }
    var x_input = inputList[0].ShapeX;
    var y_input = inputList[0].ShapeY;
    XML.BeginNode("input");
    XML.Node("shape","["+x_input.toString()+"],"+"["+y_input.toString()+"]");
    XML.Node("data",makeFileidCommaString(inputList));
    XML.EndNode();

    //console.log(visit);
    var modelList = topologicalSort(visit);

    //data_processing
    XML.BeginNode("data_processing");
    XML.Node("size",(modelList.length-1).toString());
    var seq=1;
    for(var x in modelList){
        if(modelList[x] instanceof DataPreprocessingModel){
            modelList[x].toXML(XML,seq++);
        }else continue;
    }
    XML.EndNode();

    //model
    for(var x=0; x<models.length;x++){
        if(models[x] instanceof InputModel || models[x] instanceof DataPreprocessingModel){
            continue;
        }else{
            console.log(models[x]);
            models[x].toXML(XML);
            break;
        }
    }

    XML.Close();
    console.log(XML.ToString().replace(/</g, "\n<"));
    return XML.ToString().replace(/</g, "\n<");
}



function makeFileidCommaString(list){
    var str ="";
    for(var x =0; x<list.length;x++){
        if(list[x] instanceof InputModel) {
            if (x != list.length - 1)str += list[x].fileID + ",";
            else str += list[x].fileID;
        }else if(list[x] instanceof DataPreprocessingModel){
            if (x != list.length - 1)str += "seq"+list[x].seq + ",";
            else str += "seq"+list[x].seq ;
        }
    }
    return str;
}


function topologicalSort(visit){

    var list=[];//sorted list

    //find ML model
    var startModel;
    for(var x=0; x<models.length;x++){
        if(models[x] instanceof InputModel || models[x] instanceof DataPreprocessingModel){
            continue;
        }else{
            startModel=models[x];
            break;
        }
    }
   // console.log(startModel);
    //DFS
    list.push(startModel);
    visit[getModelIdxById(startModel.ID)]=true;
    var stack=[startModel];

    var curModel =stack[stack.length-1];
    while(stack.length>0){

        if(curModel.prevModel==null || curModel.prevModel.length==0) {
            alert("not fully connected!!");
            return null;
        }
      //  console.log(stack.length);
       // console.log(curModel.prevModel);

        for(var p=0; p<curModel.prevModel.length;p++){
          //  console.log("visit : " + getModelIdxById(curModel.prevModel[p].ID));
            if(visit[getModelIdxById(curModel.prevModel[p].ID)]==true) continue;
            else{
                list.push(curModel.prevModel[p]);
                visit[getModelIdxById(curModel.prevModel[p].ID)]=true;
                stack.push(curModel.prevModel[p]);
            }
        }
        curModel=stack.pop();
    }

    //console.log(visit);
    list.reverse();
    return list;
}


//Model 좌표를 위한 xml
function makeModelXML(){

    var XML = new XMLWriter();
    XML.BeginNode("model");
    for(var x  in models){
        console.log(models[x]);
        models[x].toModelXML(XML);
    }
    XML.Close();
    console.log(XML.ToString().replace(/</g, "\n<"));
    return XML.ToString().replace(/</g, "\n<");
}

function makeCommaString(list){
    var str ="";
    for(var x =0; x<list.length;x++){
            if (x != list.length - 1)str += list[x] + ",";
            else str += list[x];
        }

    return str;
}

/////////////////////////////////////////////////////////////
////////////////Restore MODEL from  XML//////////////////////
////////////////////////////////////////////////////////////


var xxx;
var d;

function restoreModel(exp){
    //TODO : Complete
    if(exp==null) return;
    var json_exp = JSON.parse(exp);

    var xml = json_exp['xml'];
    var drawing = json_exp['drawing'];

    //string to xml
    xxx=xml=$.parseXML(xml);
    d=drawing=$.parseXML(drawing);
    console.log(xml);
    console.log(drawing);


    //restore INPUT
    var inputModels=$(xml).find('input').find('data').text().split(',');
    console.log(inputModels);
    if(inputModels.length==0) return;


    console.log("START  : INPUT MODEL RESTORE");
    for (var x in inputModels) {
        var num = inputModels[x]*1;
        var lt = $(drawing).find('InputModel').attr('fileId', num.toString()).text().split(',');
        var l = new InputModel(modelCnt++, inputModels[x], lt[0]*1, lt[1]*1);
        models.push(l);
        canvas.add(l.fabricModel);
        canvas.renderAll();

    }

    console.log("START  : INPUT MODEL END");


    console.log("START  : DATAPROCESSING MODEL RESTORE");
    //restore Processing by seq
    var processSize=$(xml).find('data_processing').find('size').text()*1;
    console.log("pre size : "+ processSize);
    for(var s=1;s<=processSize;s++){
        //find seq : s in drawing
        var cur = $(drawing).find('DataPreprocessingModel').attr("seq",s.toString()).text().split(',');
        var l = new DataPreprocessingModel(modelCnt++,cur[0],cur[1]*1,cur[2]*1);
        models.push(l);
        canvas.add(l.fabricModel);

        //connect model
        var prev = $(xml).find(l.type.toString()).attr("seq",s.toString()).find('data').text().split(',');
        for(var prevId in prev) {
            for (var idx in models) {
                if (models[idx] instanceof InputModel && model[idx].fileID == (prev[prevID]*1).toString()) {
                    selectedModel[0] = models[idx];
                    modelConnect(l);
                    break;
                }
            }
        }
        canvas.renderAll();
    }

    console.log("START  : DATAPROCESSING MODEL END");


    console.log("START  : ML MODEL START");
    //restore MODEL
     var modelType=$(xml).find('model').find('type').text();
    console.log(modelType);

    if(modelType == "linear_regression"){
        var curXY = $(drawing).find('linear_regression').text().split(',');
        var l = new Regression(modelCnt++,'linear_regression',curXY[0],curXY[1]);
        models.push(l);
        canvas.add(l.fabricModel);


    }else if(modelType == "softmax_regression"){
        var curXY = $(drawing).find('softmax_regression').text().split(',');
        var l = new Regression(modelCnt++,'softmax_regression',curXY[0],curXY[1]);
        models.push(l);
        canvas.add(l.fabricModel);

    }else if(modelType == "Polynomial regression"){
        var curXY = $(drawing).find('Polynomial regression').text().split(',');
        var l = new Regression(modelCnt++,'Polynomial regression',curXY[0],curXY[1]);
        models.push(l);
        canvas.add(l.fabricModel);

    }else if(modelType == "neural_network"){
         var curXY = $(drawing).find('NeuralNetworks').text().split(',');
        var l = new NeuralNetworks(modelCnt++,curXY[0],curXY[1]);
        models.push(l);
        canvas.add(l.fabricModel);
        l.updateFabricModel();
        makeLayerOption(1);

    }else if(modelType == "convolution_neural_network"){
        var curXY = $(drawing).find('ConvolutionNeuralNetworks').text().split(',');
        var l = new ConvolutionNeuralNetworks(modelCnt++,curXY[0],curXY[1]);
        models.push(l);
        canvas.add(l.fabricModel);
        l.updateFabricModel();
        canvas.renderAll();
        makeCNNLayerOption(1);
    }
    else{
        console.log("can not match model type");
    }
    console.log("START  : ML MODEL END");


    canvas.renderAll();

}
