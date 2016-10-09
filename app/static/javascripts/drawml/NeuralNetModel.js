/**
 * Created by koohanmo on 2016. 9. 16..
 */

/*
 NeralNetworks model
 */

function Layer(id,activation,input,output){
    this.id=id;
    this.activation = activation;
    this.input = input;
    this.output = output;

    this.makeLayer =function(){
        this.LayerContainer = new fabric.Rect({
            fill:'#ffffff',
            rx:10,
            ry:10,
            width:120,
            height:120,
            stroke:"#1788B5",
            strokeWidth:2,
        });

        this.LayerID = new fabric.Text("Layer "+this.id, {
            fontFamily: 'Comic Sans',
            fontSize: 15,
            fill :'#000000',
            textAlign:'center',
        });

        this.LayerID.set({
            left : this.LayerContainer.getWidth()/2 - this.LayerID.getWidth()/2,
            top : 10,
        });

        this.Activation = new fabric.Text(this.activation, {
            fontFamily: 'Comic Sans',
            fontSize: 15,
            fill :'#000000',
            textAlign:'center'
        });
        this.Activation.set({
            left : this.LayerContainer.getWidth()/2 - this.Activation.getWidth()/2,
            top : 10 + this.LayerContainer.getHeight()/4,
        });

        this.Input = new fabric.Text("IN : "+this.input, {
            fontFamily: 'Comic Sans',
            fontSize: 15,
            fill :'#000000',
            textAlign:'center'
        });
        this.Input.set({
            left : this.LayerContainer.getWidth()/2 - this.Input.getWidth()/2,
            top : 10 + this.LayerContainer.getHeight()/4*2,
        });

        this.Output = new fabric.Text("OUT :  "+this.output, {
            fontFamily: 'Comic Sans',
            fontSize: 15,
            fill :'#000000',
            textAlign:'center'
        });

        this.Output.set({
            left : this.LayerContainer.getWidth()/2 - this.Output.getWidth()/2,
            top : 10 + this.LayerContainer.getHeight()/4*3,
        });

        this.group = new fabric.Group([this.LayerContainer,this.LayerID,this.Activation,this.Input,this.Output], {

        });

        return this.group;
    }

    this.fabricModel = this.makeLayer();

    this.setId = function(id){
        this.id=id;
        this.fabricModel.getObjects()[1].setText('Layer ' +id);
        // this.model.item(1).set({
        //     left : -this.model.item(1).getWidth()/2,
        //     top : -this.model.item(1).getHeight()/2
        // });
        canvas.renderAll();
    }

    this.getActivation =function () {
        if(this.activation==null) return null;
        else return this.activation.toString();
    }

    this.setActivation = function (type) {
        this.activation=type;
        this.fabricModel.getObjects()[2].setText(type);
        canvas.renderAll();
    }
    this.setLayerInput = function (input) {
        this.input=input;
        this.fabricModel.getObjects()[3].setText('IN : '+input);
        canvas.renderAll();
    }
    this.setLayerOutput = function (output) {
        this.output=output;
        this.fabricModel.getObjects()[4].setText('OUT : '+output);
        canvas.renderAll();
    }

    this.toXML = function(XML,layerNtoXML){
        XML.BeginNode("layer");
        XML.Attrib("id",layerNtoXML.toString());
        XML.Node("type","none");
        XML.Node("activation",this.activation);
        XML.Node("input",this.input.toString());
        XML.Node("output",this.output.toString());
        XML.EndNode();
    }
}


//Manage Layers
function LayerSet(){

    this.layers=[new Layer(1,'relu',10,10)];
    this.fabricModel =this.layers[0].fabricModel;
    this.addLayerFrontOf =function(position){
        //Shift
        for(var x = this.layers.length; x>position;x--){
            this.layers[x] = this.layers[x-1];
            this.layers[x].setId(x+1);
        }
        var newL = new Layer(position+1,'relu',10,10);
        this.layers[position] =  newL;

        //TODO : Update Canvas UI
    }

    this.addLayerBackOf = function (position) {
        this.addLayerFrontOf(position+1);
        //TODO : Update Canvas UI
    }

    this.deleteLayer=function(position){
        if(this.layers.length ==1) return;
        this.layers.splice(position-1,1);
        for(var x=0; x<this.layers.length;x++){
            this.layers[x].setId(x+1);
        }
        //TODO : Update Canvas UI
    }

    this.fabricModel;

    this.UpdateFabric = function(){
        var newModel =new fabric.Group([], {
            left: 15,
            top : 50
        });

        for(var x =0; x<this.layers.length;x++){
            this.layers[x].fabricModel.set({
                top : 0,
                left : x* 120 + x*10
            });
            newModel.addWithUpdate(this.layers[x].fabricModel);
        }

        this.fabricModel = newModel;
    }

    this.setActivation = function (layer,type) {
        this.layers[layer-1].setActivation(type);
    }
    this.setLayerInput = function (layer,input) {
        this.layers[layer-1].setLayerInput(input);
    }
    this.setLayerOutput = function (layer,output) {
        this.layers[layer-1].setLayerOutput(output);
    }

    this.toXML = function(XML){
        XML.BeginNode("layer_set");
        XML.Node("size",this.layers.length.toString());
        for(var x=0; x<this.layers.length;x++){
            this.layers[x].toXML(XML,x+1);
        }
        XML.EndNode();
    }


}


function NeuralContainer(layerN){
    this.AlgoritmContainer = new fabric.Rect({
        fill:'#ffffff',
        rx:10,
        ry:10,
        width:120+130*(layerN),
        height:250,
        stroke:"#1788B5",
        strokeWidth:2,
    });

    this.Algoname = new fabric.Text("Neural Network", {
        top:10,
        fontFamily: 'Comic Sans',
        fontSize: 30,
        fill :'#008C9E',
        textAlign:'center',
    });

    //객체 생성 후에, 가운데정렬
    this.Algoname.set({
        left : this.AlgoritmContainer.getWidth()/2 - this.Algoname.getWidth()/2,
    });

    this.group = new fabric.Group([this.AlgoritmContainer,this.Algoname], {

    });

    return this.group;

}


function NeuralNetworks(id,pointLeft, pointTop){
    this .type = "neural_network"
    this.layerSet=new LayerSet();
    this.initializer = new Initializer('random_uniform');
    this.optimizer = new Optimizer('gradient_descent');
    this.regularization = new Regularization();
    this.training_epoch = 1024;
    this.container=null;
    this.ID=id;

    this.getContainer= function(){
        this.container = new NeuralContainer(this.layerSet.layers.length);
        return this.container;
    }

    this.fabricModel= new fabric.Group([this.getContainer(),this.layerSet.fabricModel], {
        left:pointLeft,
        top:pointTop
    });
    this.fabricModel.id=this.ID;

    this.updateFabricModel = function(){
        this.layerSet.UpdateFabric();
        this.layerSet.fabricModel.set({
            left:60,
            top:75
        });
        var replaceModel = new fabric.Group([this.getContainer(),this.layerSet.fabricModel], {
            left:this.fabricModel.left,
            top:this.fabricModel.top
        });
        canvas.remove(this.fabricModel);
        this.fabricModel = replaceModel;
        this.fabricModel.id=this.ID;
        this.fabricModel.on('selected',function(options){
            currentSelectedModel=getModelById(this.id);
            currentSelectedModel.changeOptionMenu();
            modelConnect(currentSelectedModel);
            clearConnectModelDelete();
        });

        this.fabricModel.on('moving',function (options) {
            currentSelectedModel=getModelById(this.id);
            trackingModel(currentSelectedModel);
        });
        trackingModel(currentSelectedModel);
        canvas.add(this.fabricModel);
        canvas.renderAll();
    }

    this.fabricModel.on('selected',function(options){
        currentSelectedModel=getModelById(this.id);
        currentSelectedModel.changeOptionMenu();
        modelConnect(currentSelectedModel);
        clearConnectModelDelete();
    });

    this.fabricModel.on('moving',function (options) {
        currentSelectedModel=getModelById(this.id);
        trackingModel(currentSelectedModel);
    });

    this.changeOptionMenu =function () {

        clearDataShapeOption();

        //Set Initializer
        $('#initializer-btn').show();
        var iniType = this.initializer.type;
        $('#change-Initializer-current').text(iniType);
        if(iniType=='random_uniform'){
            $('#change-Initializer-value').hide();
            $('#change-Initializer-value-max').show();
            $('#change-Initializer-value-min').show();
        }else if(iniType=='random_normal'){
            $('#change-Initializer-value').show();
            $('#change-Initializer-value-max').hide();
            $('#change-Initializer-value-min').hide();
        }
        $('#change-Initializer-value-max-input').val(this.initializer.max);
        $('#change-Initializer-value-min-input').val(this.initializer.min);
        $('#change-Initializer-value-input').val(this.initializer.val);

        //Set Optimizer
        $('#optimizer-btn').show();
        $('#change-Optimizer-current').text(this.optimizer.type);
        $('#change-Optimizer-learningRate-input').val(this.optimizer.learningRate);

        //Set Regularization
        $('#regularization-btn').show();
        $('#change-regularization-current').text(this.regularization.enable);
        if(this.regularization=="false"){
            $('#change-regularization-lambda').hide();
        }else{
            $('#change-regularization-lambda').show();
        }
        $('#change-regularization-lambda-input').val(this.regularization.lambda);
        //Set trainingEpoch
        $('#trainingEpoch-btn').show();
        $('#change-trainingEpoch-input').val(this.training_epoch);


        //TODO Layer 반영
        clearLayerOption();
        for(var x =0; x<this.layerSet.layers.length;x++) makeLayerOption(x+1);
        $('#model-addlayer-btn').show();

        //TODO 옵션!
    }


    this.addLayerFrontOf = function(position){

        this.layerSet.addLayerFrontOf(position);
        this.layerSet.UpdateFabric();
        this.updateFabricModel();

    }

    this.addLayerBackOf = function(position){
        this.layerSet.addLayerBackOf(position);
        this.layerSet.UpdateFabric();
        this.updateFabricModel();
    }

    this.deleteLayer = function (position) {
        this.layerSet.deleteLayer(position);
        this.layerSet.UpdateFabric();
        this.updateFabricModel();
        this.changeOptionMenu();
    }


    this.getLayerLength = function(){
        return this.layerSet.layers.length;
    }


    //change Initializer
    this.changeInitializer =function (type) {
        this.initializer.changeType(type);
    }

    //change Optimizer
    this.changeOptimizer =function(type){
        this.optimizer.changeOptimizer(type);
    }

    //change Regularization
    this.setRegularizationEnable =function (can) {
        this.regularization.changeEnable(can);
    }

    this.setLambda = function(val){
        this.regularization.changeLambda(val);
    }

    //change training epoch
    this.changeTrainingEpoch =function (val) {
        this.training_epoch=val;
    }

    this.setActivation = function (layer,type) {
        this.layerSet.setActivation(layer,type);
    }
    this.setLayerInput = function (layer,input) {
        this.layerSet.setLayerInput(layer,input);
    }
    this.setLayerOutput = function (layer,output) {
        this.layerSet.setLayerOutput(layer,output);
    }

    this.toXML =  function(XML)
    {
        try
        {
            XML.BeginNode("model");

            if(this.prevModel==null ||this.prevModel.length==0){
                alert("Model hasn't Input Data");
            }

            if(this.prevModel[0] instanceof InputModel){
                XML.Node("data",this.prevModel[0].fileID.toString());
            }else if(this.prevModel[0] instanceof DataPreprocessingModel){
                XML.Node("data",'seq'+this.prevModel[0].seq.toString());
            }

                XML.Node("type", "neural_network");
                this.layerSet.toXML(XML);
                this.initializer.toXML(XML);
                this.optimizer.toXML(XML);
                this.regularization.toXML(XML);
                XML.Node("training_epoch",this.training_epoch.toString());
            XML.EndNode();
        }
        catch(Err)
        {
            alert("Error: " + Err.description);
        }
        return true;
    }

    this.toModelXML = function(XML){
        try
        {
            var list = [this.fabricModel.left,this.fabricModel.top];
            XML.Node("NeuralNetworks", makeCommaString(list));
        }
        catch(Err)
        {
            alert("Error: " + Err.description);
        }
        return true;
    }


}

function makeLayerOption(LayerNumber){
    var option = $('#btn-dummy').clone(true);
    var optionLayer = $('#dummyLayer').clone(true);
    option.attr('id','btn-layer'+LayerNumber.toString()).show();
    option.html('Layer'+LayerNumber.toString());
    option.attr('data-target','#layer'+LayerNumber.toString());
    optionLayer.attr('id','layer'+LayerNumber.toString());
    optionLayer.addClass('collapse');
    $('#model-addlayer-btn').before(option);
    $('#model-addlayer-btn').before(optionLayer);

    //Event Handling
    var btngroup= optionLayer.children().eq(0);
    btngroup.find('a').click(function(){
        btngroup.find('button').text($(this).text());
        currentSelectedModel.setActivation(LayerNumber,$(this).text());
    });

    var inputDiv =optionLayer.children().eq(1).find('input');
    inputDiv.on("change paste keyup", function() {
        currentSelectedModel.setLayerInput(LayerNumber,$(this).val());
    });

    var outputDiv =optionLayer.children().eq(2).find('input');
    outputDiv.on("change paste keyup", function() {
        currentSelectedModel.setLayerOutput(LayerNumber,$(this).val());
    });

    var delBtn =optionLayer.children().eq(3);
    delBtn.click(function(){
        currentSelectedModel.deleteLayer(LayerNumber);
        if(LayerNumber!=1) {
            option.hide();
            optionLayer.hide();
        }
    });


    //Read data
    if(currentSelectedModel.layerSet.layers.length >=LayerNumber) {
        btngroup.find('button').text(currentSelectedModel.layerSet.layers[LayerNumber - 1].getActivation());
        inputDiv.val(currentSelectedModel.layerSet.layers[LayerNumber - 1].input);
        outputDiv.val(currentSelectedModel.layerSet.layers[LayerNumber - 1].output);
    }
}


function clearLayerOption(){
    //NN 관련  UI 삭제
    var curUI = $('#trainingEpoch-btn');
    curUI.nextAll().filter('.layer').remove();
    $('#model-addlayer-btn').hide();
}





