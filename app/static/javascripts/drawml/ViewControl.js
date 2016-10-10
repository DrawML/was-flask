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
        if(datalist[x].id==id){
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

function printResultMsg(msg) {
    $('#footer-result-msg').text(msg);

    setTimeout(function () {$('#footer-result-msg').text('');}, 5000);
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
    }else if(ui.draggable.attr('id')=="LogisticRegression"){
        if(!canMLmodel()) {
            alert("Already have ML model...!");
            return;
        }
        clearDataShapeOption();
        clearLayerOption();
        makeDefaultOptions()
        var l = new Regression(modelCnt++,'logistic_regression',canvasX-wi-150,canvasY-ContainerTop);
        models.push(l);
        currentSelectedModel=l;
        canvas.add(l.fabricModel);
        canvas.renderAll();
    }
    else if(ui.draggable.attr('id')=="SoftMaxRegression"){
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

    $('#footer-Save-btn').click(function (e) {

        var exp_xml=makeXML();
        var model_xml=makeModelXML();

        if(XMLValidation==false){
            alert('Experiment is not Valid!!');
            e.preventDefault();
            return;
        }
        XMLValidation=true;

        var exp_data=new Object();
        exp_data.drawing = model_xml;
        exp_data.xml = exp_xml;
        var x = new Object();
        x.exp_data=exp_data;
        var jsonInfo = JSON.stringify(x);

        console.log(jsonInfo);
        update_exp(jsonInfo);
    });

    //Models To XML
    $('#footer-toxml-btn').click(function (e) {
        if(isProcessing) return;

        var exp_xml=makeXML();
        var model_xml=makeModelXML();

         if(XMLValidation==false){
            alert('Experiment is not Valid!!');
             e.preventDefault();
             return;
        }
        XMLValidation=true;

        var exp_data=new Object();
        exp_data.drawing = model_xml;
        exp_data.xml = exp_xml;
        var x = new Object();
        x.exp_data=exp_data;
        var jsonInfo = JSON.stringify(x);

        console.log(jsonInfo);

        var callback = function () {
            run_exp(exp_xml);
        };

        update_exp(jsonInfo, callback);
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
        for(var x in models){
            if(models[x] instanceof InputModel)
                models[x].changeShapeX($(this).val());
        }

    });
    $('#change-datashape-y-input').on("change paste keyup", function() {
        for(var x in models){
            if(models[x] instanceof InputModel)
                models[x].changeSHapeY($(this).val());
        }
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


var XMLValidation =true;
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
        XMLValidation=false;
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
        if(models[x] instanceof InputModel){
            continue;
        }else{
            if(models[x].nextModel==null || models[x].nextModel.length==0)
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
            XMLValidation=false;
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

    //Input...
    for(var x  in models){
        if(models[x] instanceof InputModel) {
            models[x].toModelXML(XML);
        }
    }

    //data preprocessing
    var processCnt =0;

    for(var x  in models){
        if(models[x] instanceof DataPreprocessingModel) {
            processCnt+=1;
        }
    }
    for(var seq=1; seq<=processCnt;seq++) {
        for (var x  in models) {
            if (models[x] instanceof DataPreprocessingModel && models[x].seq==seq) {
                models[x].toModelXML(XML);
            }
        }
    }

    //model
    for(var x  in models){
        if(models[x] instanceof InputModel || models[x] instanceof DataPreprocessingModel) continue;
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

function restoreModel(exp) {
    //TODO : Complete
    if (exp == null) return;
    var json_exp = JSON.parse(exp);

    var xml = json_exp['xml'];
    var drawing = json_exp['drawing'];
    console.log(xml);
    console.log(drawing);


    //string to xml
    xxx = xml = $.parseXML(xml);
    d = drawing = $.parseXML(drawing);
    console.log(xml);
    console.log(drawing);

    if(xml=="" || xml==null) return;
    if($(drawing).find('position').length !=0) return;

    var shp = $(xml).find('shape').text().split(',');
    var shp_x = shp[0].trim().substring(1,shp[0].length-1);
    var shp_y = shp[1].trim().substring(1,shp[1].length-2);

    if ($(xml).text() == "") return;

    //restore INPUT
    var inputModels = $(xml).find('input').find('data').text().split(',');
    console.log(inputModels);
    if (inputModels.length == 0) return;


    console.log("START  : INPUT MODEL RESTORE");
    for (var x in inputModels) {
        var num = inputModels[x] * 1;
        console.log(getDataNameById(num * 1));
        console.log(inputModels[x]);

        var lt = $(drawing).find('InputModel').attr('fileId', num.toString())[0];
        lt=$(lt).text().split(',');
        console.log(lt);

        var l = new InputModel(modelCnt++, getDataNameById(num.toString()), inputModels[x] * 1, lt[0] * 1, lt[1] * 1);
        l.ShapeX = shp_x;
        l.ShapeY = shp_y;
        models.push(l);
        canvas.add(l.fabricModel);
        canvas.renderAll();
        $(drawing).find('InputModel').attr('fileId', num.toString())[0].remove();
    }

    console.log("START  : INPUT MODEL END");


    console.log("START  : DATAPROCESSING MODEL RESTORE");
    //restore Processing by seq
    var processSize = $(xml).find('data_processing').find('size').text() * 1;
    console.log("pre size : " + processSize);
    var processList=[];
    for (var s = 1; s <= processSize; s++) {
        //find seq : s in drawing
        var cur = $($(drawing).find('DataPreprocessingModel')[s-1]).text().split(',');
        var l = new DataPreprocessingModel(modelCnt++, cur[0], cur[1] * 1, cur[2] * 1);
        l.seq = s;
        models.push(l);
        processList.push(l);
        canvas.add(l.fabricModel);
        canvas.renderAll();
    }

    //connect preprocessing model
    for (var s = 1; s<=processSize;s++){
        var dp=$(xml).find('data_processing').children();
        dp=$(dp)[s];
        var prev = $(dp).find('data').text().split(',');
        console.log(prev);
        for (var prevId in prev) {
            var curID = prev[prevId].trim();
            var isSeq=false;
            if(curID.length>=4 && curID.substring(0,3)=="seq"){
                isSeq=true;
                curID=curID.substring(3,curID.length)*1;
            }
            console.log("CUR ID : "+ curID);
            console.log("isSEQ : " +isSeq)
            for (var idx =0; idx<models.length ;idx++) {
                if (!isSeq && models[idx] instanceof InputModel && models[idx].fileID == curID*1) {
                    console.log("Connect To INPUT");
                    if(models[idx].nextModel!=null && models[idx].nextModel.length>=1) continue;
                    console.log("Connect : !!!!!!!!! INPUT!!");
                    makingModel = true;
                    modelConnect(models[idx]);
                    modelConnect(processList[s-1]);
                    makingModel = false;
                    break;
                } else if (isSeq && models[idx] instanceof DataPreprocessingModel && models[idx].seq ==curID*1) {
                    console.log("Connect To DATAPREPRO");
                    if(models[idx].nextModel!=null && models[idx].nextModel.length>=1) continue;
                    console.log("Connect : !!!!!!!!! INPUT!!");
                    makingModel = true;
                    modelConnect(models[idx]);
                    modelConnect(processList[s-1]);
                    makingModel = false;
                    break;
                }
            }
        }
    }

    console.log("START  : DATAPROCESSING MODEL END");


    console.log("START  : ML MODEL START");
    //restore MODEL
    var modelType = $(xml).find('model').find('type')[0];
    modelType = $(modelType).text().trim();
    console.log(modelType);
    var ML;
    if (modelType != null && modelType != "") {
        if (modelType == "linear_regression" || modelType == "softmax_regression" || modelType == "Polynomial regression" || modelType=="logistic_regression") {
            var curXY = $(drawing).find(modelType).text().split(',');
            ML = new Regression(modelCnt++, curXY[0], curXY[1] * 1, curXY[2] * 1);
            models.push(ML);
            canvas.add(ML.fabricModel);
        } else if (modelType == "neural_network") {
            var curXY = $(drawing).find('NeuralNetworks').text().split(',');
            ML = new NeuralNetworks(modelCnt++, curXY[0] * 1, curXY[1] * 1);
            models.push(ML)
            canvas.add(ML.fabricModel);
            currentSelectedModel = ML;
            ML.updateFabricModel();
            makeLayerOption(1);

            //Connect Layer , Layer Option
            currentSelectedModel = ML;

            //레이어 갯수 맞추기
            var layerN = $(xml).find('layer_set').find('size').text() * 1;
            for (var x = 0; x < layerN - 1; x++) {
                makeLayerOption(ML.getLayerLength() + 1);
                ML.addLayerBackOf(ML.getLayerLength() - 1);
            }
            //자리 재조정.
            ML.fabricModel.set({
                left: curXY[0] * 1,
                top: curXY[1] * 1
            });

            //레이어 옵션적용
            var layer_xml = $(xml).find('layer');
            for (var x = 0; x < layerN; x++) {
                //var layer_type = $(layer_xml).find('type').text().trim();
                var layer_acti = $(layer_xml[x]).find('activation').text().trim();
                var layer_input = $(layer_xml[x]).find('input').text().trim() * 1;
                var layer_output = $(layer_xml[x]).find('output').text().trim() * 1;

                ML.setActivation(x+1, layer_acti);
                ML.setLayerInput(x+1, layer_input);
                ML.setLayerOutput(x+1, layer_output);
            }
            ML.updateFabricModel();

        } else if (modelType == "convolution_neural_network") {
            var curXY = $(drawing).find('ConvolutionNeuralNetworks').text().split(',');
            ML = new ConvolutionNeuralNetworks(modelCnt++, curXY[0] * 1, curXY[1] * 1);
            models.push(ML);
            canvas.add(ML.fabricModel);
            currentSelectedModel = ML;
            ML.updateFabricModel();
            canvas.renderAll();
            makeCNNLayerOption(1);


            //Connect Layer , Layer Option
            currentSelectedModel = ML;

            //레이어 갯수 맞추기
            var layerN = $(xml).find('layer_set').find('size').text() * 1;
            for (var x = 0; x < layerN - 3; x++) {
                makeCNNLayerOption(ML.getLayerLength() + 1);
                ML.addLayerBackOf(ML.getLayerLength() - 1);
            }
            //자리 재조정.
            ML.fabricModel.set({
                left: curXY[0] * 1,
                top: curXY[1] * 1
            });

            //레이어 옵션적용
            var dp_conv = $(xml).find('dropout_conv').text()*1;
            var dp_hidden = $(xml).find('dropout_hidden').text()*1;

            ML.dropOut.conv=dp_conv;
            ML.dropOut.hidden=dp_hidden;

            var layer_xml = $(xml).find('layer');
            for (var x = 0; x < layerN; x++) {
                var layer_type = $($(layer_xml[x]).find('type')[0]).text().trim();
                if(layer_type == "convolution") {
                    var layer_acti = $(layer_xml[x]).find('activation');
                    var layer_acti_type = $(layer_acti).find('type').text().trim();
                    var layer_acti_sv = $(layer_acti).find('strides_vertical').text() * 1;
                    var layer_acti_sh = $(layer_acti).find('strides_horizontal').text() * 1;
                    var layer_acti_pad = $(layer_acti).find('padding').text().trim();

                    var layer_pooling = $(layer_xml[x]).find('pooling');
                    var layer_pooling_type = $(layer_pooling).find('type').text().trim();
                    var layer_pooling_sv = $(layer_pooling).find('strides_vertical').text() * 1;
                    var layer_pooling_sh = $(layer_pooling).find('strides_horizontal').text() * 1;
                    var layer_pooling_pad = $(layer_pooling).find('padding').text().trim();

                    var layer_input_x = $(layer_xml[x]).find('input_x').text().trim() * 1;
                    var layer_input_y = $(layer_xml[x]).find('input_y').text().trim() * 1;
                    var layer_input_z = $(layer_xml[x]).find('input_z').text().trim() * 1;
                    var layer_output = $(layer_xml[x]).find('output').text().trim() * 1;


                    ML.setActivationType(x + 1, layer_acti_type);
                    ML.setActivationSV(x + 1, layer_acti_sv);
                    ML.setActivationSH(x + 1, layer_acti_sh);
                    ML.setActivationPadding(x + 1, layer_acti_pad);

                    ML.setPoolingType(x + 1, layer_pooling_type);
                    ML.setPoolingSV(x + 1, layer_pooling_sv);
                    ML.setPoolingSH(x + 1, layer_pooling_sh);
                    ML.setPoolingPadding(x + 1, layer_pooling_pad);

                    ML.setLayerInputX(x + 1, layer_input_x);
                    ML.setLayerInputY(x + 1, layer_input_y);
                    ML.setLayerInputZ(x + 1, layer_input_z);
                    ML.setLayerOutput(x + 1, layer_output);
                }else if(layer_type == "none"){

                    var layer_acti = $(layer_xml[x]).find('activation').text().trim();
                    var layer_input = $(layer_xml[x]).find('input').text().trim() * 1;
                    var layer_output = $(layer_xml[x]).find('output').text().trim() * 1;

                    ML.layerSet.mergeLayer.activation=layer_acti;
                    ML.layerSet.mergeLayer.input=layer_input;
                    ML.layerSet.mergeLayer.output=layer_output;

                }else if(layer_type == "out"){
                    var layer_acti = $(layer_xml[x]).find('activation').text().trim();
                    var layer_input = $(layer_xml[x]).find('input').text().trim() * 1;
                    var layer_output = $(layer_xml[x]).find('output').text().trim() * 1;

                    ML.layerSet.outLayer.activation=layer_acti;
                    ML.layerSet.outLayer.input=layer_input;
                    ML.layerSet.outLayer.output=layer_output;
                }
            }
            ML.updateFabricModel();
        }
        else {
            console.log("can not match model type");
        }

        //Attach Common Option

        //Initializer


        var initializer = $(xml).find('initializer');
        var init_type = $(initializer).find('type').text().trim();
        var initTemp = ML.initializer;
        ML.changeInitializer(init_type);
        if (init_type == 'random_normal') {
            var stddev = $(initializer).find('stddev').text() * 1;
            initTemp.val = stddev;
        } else if (init_type == 'random_uniform') {
            var init_min = $(initializer).find('min').text() * 1;
            var init_max = $(initializer).find('max').text() * 1;
            initTemp.min = init_min;
            initTemp.max = init_max;
        }

        //Optimizer

        var opti_xml = $(xml).find('optimizer');
        var opti_type = $(opti_xml).find('type').text().trim();
        var opti_rate = $(opti_xml).find('learning_rate').text() * 1;

        ML.changeOptimizer(opti_type);
        ML.optimizer.changeLearningRate(opti_rate);


        //regularization
        var regul_xml = $(xml).find('regularization');
        var regul_bool = $(regul_xml).find('enable').text().trim();
        ML.regularization.changeEnable(regul_bool);
        if (regul_bool == "true") {
            var regul_lambda = $(regul_xml).find('lambda').text() * 1;
            ML.regularization.changeLambda(regul_lambda);
        }

        //training_epoch
        var training_val = $(xml).find('training_epoch').text() * 1;
        ML.training_epoch = training_val;


        //Connect Prev Model.....
        var modelData = $(xml).find('model').find('data').text().trim();
        if (modelData.length >= 4 && modelData.substring(0, 3) == "seq") {
            //PreProcessing과 연결
            modelData = modelData.substring(3, modelData.length) * 1;
        }
        console.log("Model DATA  : " + modelData);
        for (var idx in models) {
            if (models[idx] instanceof InputModel && models[idx].fileID == modelData*1) {
                console.log("Connect To INPUT");
                makingModel = true;
                modelConnect(models[idx]);
                modelConnect(ML);
                makingModel = false;
            } else if (models[idx] instanceof DataPreprocessingModel && models[idx].seq == modelData*1) {
                console.log("Connect To DATAPREPRO");
                makingModel = true;
                modelConnect(models[idx]);
                modelConnect(ML);
                makingModel = false;
            }
        }

        currentSelectedModel = ML;
        ML.changeOptionMenu();
        console.log("START  : ML MODEL END");
    }
    canvas.renderAll();
}


