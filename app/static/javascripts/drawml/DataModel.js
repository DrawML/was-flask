//FabricModel
function getDataContainer(type) {
    this.DataContainer = new fabric.Rect({
        fill:'#ffffff',
        rx:10,
        ry:10,
        width:200,
        height:75,
        stroke:"#1788B5",
        strokeWidth:2,
    });

    this.processName = new fabric.Text(type, {
        top:10,
        fontFamily: 'Comic Sans',
        fontSize: 20,
        fill :'#2A314F',
        textAlign:'center',
    });

    //객체 생성 후에, 가운데정렬
    this.processName.set({
        left : this.DataContainer.getWidth()/2 - this.processName.getWidth()/2,
        top : this.DataContainer.getHeight()/2 - this.processName.getHeight()/2
    });

    this.group = new fabric.Group([this.DataContainer,this.processName], {

    });

    return this.group;
}

function DataPreprocessingModel(id,type,pointLeft, pointTop){
    //Concat
    //Transpose
    this.ID=id;
    this.type =type;
    this.preseq=null;

    this.fabricModel=getDataContainer(this.type);
    this.fabricModel.set({
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
        clearDefaultOptions();
        clearLayerOption();
    }

    this.toXML =  function(XML,seq)
    {
        this.seq=seq;
        try
        {
            this.seq=seq;
            XML.BeginNode(this.type.toString());
            XML.Attrib("seq",seq.toString());
            XML.Node("data", makeFileidCommaString(this.prevModel));
            XML.EndNode();
        }
        catch(Err)
        {
            alert("Error: " + Err.description);
            XMLValidation=false;
        }
        return true;
    }

    this.toModelXML = function(XML){
        try
        {
            var list = [this.type,this.fabricModel.left,this.fabricModel.top];
            XML.BeginNode("DataPreprocessingModel");
            XML.Attrib("seq",this.seq.toString());
            XML.WriteString(makeCommaString(list));
            XML.EndNode();
        }
        catch(Err)
        {
            alert("Error: " + Err.description);
            XMLValidation=false;
        }
        return true;
    }
}

function InputModel(id,fileName,fileID,pointLeft, pointTop){
    this.ID=id;
    this.ShapeX=1;
    this.ShapeY=1;
    this.fileID =fileID;
    this.fileName=fileName;
    if(this.fileName.length >=16) this.fileName=this.fileName.substring(0,16)+'...';

    this.fabricModel=getDataContainer(this.fileName);
    this.fabricModel.set({
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
        makeDataShapeOption();
        $('#change-datashape-x-input').val(currentSelectedModel.ShapeX);
        $('#change-datashape-y-input').val(currentSelectedModel.ShapeY);
        clearDefaultOptions();
        clearLayerOption();
    }

    this.changeShapeX=function(val){
        this.ShapeX=val;
    }

    this.changeSHapeY = function(val){
        this.ShapeY=val;
    }

    this.toModelXML = function(XML){
        try
        {
            var list = [this.fabricModel.left,this.fabricModel.top];
            XML.BeginNode("InputModel");
            XML.Attrib("fileId",this.fileID.toString());
            XML.WriteString(makeCommaString(list));
            XML.EndNode();
        }
        catch(Err)
        {
            alert("Error: " + Err.description);
            XMLValidation=false;
        }
        return true;
    }

}

function clearDataShapeOption(){
    $('#datashape-btn').hide();
    $('#div-datashape').collapse("hide");
}

function makeDataShapeOption(){
    $('#datashape-btn').show();
    $('#datashape-btn').addClass('collapsed');

}

