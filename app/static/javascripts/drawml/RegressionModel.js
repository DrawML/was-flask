/**
 * Created by koohanmo on 2016. 9. 16..
 */

/*
 Fabric Container Models
 * */

function getContainer(algorithmName) {
    this.AlgoritmContainer = new fabric.Rect({
        fill:'#ffffff',
        rx:10,
        ry:10,
        width:300,
        height:200,
        stroke:"#1788B5",
        strokeWidth:2,
    });

    this.Algoname = new fabric.Text(algorithmName, {
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

function getOptionContainer(opName,type){
    this.OptionContainer = new fabric.Rect({
        fill:'#014077',
        rx:10,
        ry:10,
        width:270,
        height:30,
        stroke:"#1788B5",
        strokeWidth:2,
    });

    this.OptionName = new fabric.Text(opName, {
        fontFamily: 'Comic Sans',
        fontSize: 20,
        fill :'#ffffff',
        textAlign:'center'
    });

    //객체 생성 후에, 가운데정렬
    this.OptionName.set({
        left : this.OptionContainer.getWidth()/2 - this.OptionName.getWidth()/2,
        top : this.OptionContainer.getHeight()/2 - this.OptionName.getHeight()/2,
    });

    this.group = new fabric.Group([this.OptionContainer,this.OptionName], {
        left: 15,
        top: type=='optimizer'? 150:100
    });

    return this.group;
}




/*
 Initializer Objects
 * */

function Initializer(type){

    this.type = type;
    this.model = new getOptionContainer(type,'init');
    this.min=-1.0;
    this.max=1.0;
    this.val=1.0;

    this.changeType =function(type){
        this.type=type;
        this.model.item(1).setText(this.type);
        this.model.item(1).set({
            left : -this.model.item(1).getWidth()/2,
            top : -this.model.item(1).getHeight()/2
        });
        canvas.renderAll();

    }
    this.changeVal =function(val){
        this.val=val;
    }

    this.changeMinMax = function (min,max) {
        this.min=min;
        this.max=max;
        // this.model.item(1).setText(this.type+" "+min+"~"+max);
        // this.model.item(1).set({
        //     left : -this.model.item(1).getWidth()/2,
        //     top : -this.model.item(1).getHeight()/2
        // });
    }

    //ToXml
    this.toXML = function(XML){
        XML.BeginNode("initializer");
        XML.Node("type",this.type);
        if(this.type == 'random_uniform'){
            XML.Node("min",this.min.toString());
            XML.Node("max",this.max.toString());
        }
        else if(this.type == 'random_normal'){
            XML.Node("value",this.val.toString());
        }
        XML.EndNode();
    }

}

/*
 Optimizer Model
 * */
function Optimizer(type){
    this.type = type;
    this.model = new getOptionContainer(this.type,'optimizer');
    this.learningRate =0.01;

    this.changeOptimizer = function (opti) {
        this.type = opti;
        this.model.item(1).setText(this.type);
        this.model.item(1).set({
            left : -this.model.item(1).getWidth()/2,
            top : -this.model.item(1).getHeight()/2
        });
        canvas.renderAll();
    }

    this.changeLearningRate = function(rate){
        this.learningRate=rate;
    }

    //ToXml
    this.toXML = function(XML){
        XML.BeginNode("optimizer");
        XML.Node("type",this.type);
        XML.Node("learning_rate",this.learningRate.toString());
        XML.EndNode();
    }
}
/*
 Regularization
 */
function Regularization(){

    this.enable = 'false';
    this.lambda=0;

    this.changeEnable=function(can){
        this.enable=can;
    }
    this.changeLambda = function(val){
        this.lambda=val;
    }

    this.toXML = function(XML){
        XML.BeginNode("regularization");
        XML.Node("enable",this.enable.toString());
        if(this.enable=='true') XML.Node("lambda",this.lambda.toString());
        XML.EndNode();
    }

}

/*
 Last Models
 */
function Regression(id,type,pointLeft, pointTop){

    this.ID=id;
    this.type = type;
    this.initializer = new Initializer('random_uniform');
    this.optimizer = new Optimizer('gradient descent');
    this.regularization = new Regularization();
    this.training_epoch = 1024;

    //fabric model
    this.fabricModel=new fabric.Group([getContainer(this.type),
            this.initializer.model,this.optimizer.model]
        ,{
            left: pointLeft,
            top : pointTop
        });
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

    this.changeOptionMenu =function () {
        clearDataShapeOption();
        clearLayerOption();

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

        //TODO : 다른 CNN,RNN등 모델들이 추가가 되었을 때. 나머지 옵션이 안보이게 처리해야됨.
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


    this.writeToObject =function () {

    }

    //makeXML
    this.toXML =  function(XML)
    {
        try
        {

            XML.BeginNode("model");

            if(this.prevModel==null ||this.prevModel.length==0){
                alert("Model hasn't Input Data");
            }

            if(this.prevModel[0] instanceof InputModel){
                XML.Node("data",prevModel[0].fileID.toString());
            }else if(this.prevModel[0] instanceof DataPreprocessingModel){
                XML.Node("data",'seq'+prevModel[0].seq.toString());
            }
            console.log("Find prevModel.........!!!");

            XML.Node("type", this.type);
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
            var list = [this.type,this.fabricModel.left,this.fabricModel.top];
            XML.Node(this.type, makeCommaString(list));
        }
        catch(Err)
        {
            alert("Error: " + Err.description);
        }
        return true;
    }

    this.changeOptionMenu();


}

function clearDefaultOptions(){
    $('#initializer-btn').hide();
    $('#div-initializer').collapse("hide");
    $('#optimizer-btn').hide();
    $('#div-optimizer').collapse("hide");
    $('#regularization-btn').hide();
    $('#div-regularization').collapse("hide");
    $('#trainingEpoch-btn').hide();
    $('#div-trainingepoch').collapse("hide");
}
function makeDefaultOptions(){
    $('#initializer-btn').show();
    $('#initializer-btn').addClass('collapsed');
    $('#optimizer-btn').show();
    $('#optimizer-btn').addClass('collapsed');
    $('#regularization-btn').show();
    $('#regularization-btn').addClass('collapsed');
    $('#trainingEpoch-btn').show();
    $('#trainingEpoch-btn').addClass('collapsed');
}