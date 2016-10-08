/**
 * Created by 구한모 on 2016-09-30.
 */

function _createArrowHead(points) {
    var headLength = 15,

    x1 = points[0],
    y1 = points[1],
    x2 = points[2],
    y2 = points[3],

    dx = x2 - x1,
    dy = y2 - y1,

    angle = Math.atan2(dy, dx);

    angle *= 180 / Math.PI;
    angle += 90;

    var triangle = new fabric.Triangle({
        angle: angle,
        fill: '#207cca',
        top: y2,
        left: x2,
        height: headLength,
        width: headLength,
        originX: 'center',
        originY: 'center',
        selectable: false
    });

    return triangle;
}


function createLineArrow(startModel,endModel) {

    this.points=[];
    this.makePoints =function (startModel, endModel){
        var x1 = startModel.fabricModel.left + startModel.fabricModel.getWidth()/2;
        var y1 = startModel.fabricModel.top  + startModel.fabricModel.getHeight();

        var x2 = endModel.fabricModel.left + endModel.fabricModel.getWidth()/2;
        var y2 = endModel.fabricModel.top;

        this.points =[x1,y1,x2,y2];
        return  [x1, y1, x2, y2];
    }

    this.makePoints(startModel,endModel);

    this.line = new fabric.Line(this.points, {
        strokeWidth: 5,
        stroke: '#7db9e8',
        originX: 'center',
        originY: 'center',
        lockMovementX : true,
        lockMovementY : true,
        hasControls: false,
        hasBorders: true,
        hasRotatingPoint: false,
        hoverCursor: 'default',
        selectable: true
    });

    this.line.startModel = startModel;
    this.line.endModel = endModel;

    this.line.on('selected',function(options){
        makeConnectModelDelete();
        currentSelectedArrow = this;
    });

    this.triangle =_createArrowHead(this.points);
    this.line.triangle=this.triangle;
}


function LineArrow(startModel,endModel){

    this.startModel = startModel;
    this.endModel = endModel;

    this.fabricModel = new createLineArrow(startModel,endModel);

    this.changePoint = function (startModel,endModel) {
        this.deleteFabric();
        this.fabricModel = new createLineArrow(startModel,endModel);
        canvas.add(this.fabricModel.line);
        canvas.add(this.fabricModel.triangle);
        canvas.renderAll();
    }

    this.changeStartModel = function (startModel) {
        this.startModel=startModel;
        this.changePoint(this.startModel,this.endModel);
    }
    this.changeEndModel = function(endModel){
        this.endModel=endModel;
        this.changePoint(this.startModel,this.endModel);
    }


    this.deleteFabric = function () {
        canvas.remove(this.fabricModel.triangle);
        canvas.remove(this.fabricModel.line);
    }
    canvas.add(this.fabricModel.line);
    canvas.add(this.fabricModel.triangle);
    canvas.renderAll();
}


//선택된 Line 제거
function deleteLineArrow(){
    if(currentSelectedArrow==null) return;
    if(currentSelectedArrow.startModel==null) return;
    if(currentSelectedArrow.endModel ==null) return;

    var sModel =currentSelectedArrow.startModel;
    var eModel = currentSelectedArrow.endModel;

    //sModel.nextLine 순회
    var idx=0;
    for(;idx<sModel.nextLine.length;idx++){
        if(sModel.nextLine[idx].startModel == sModel && sModel.nextLine[idx].endModel==eModel) {
            sModel.nextLine.splice(idx,1);
            sModel.nextModel.splice(idx,1);
        }
    }


    //eModel.prevLine 순회
    idx=0;
    for(;idx<eModel.prevLine.length;idx++){
        if(eModel.prevLine[idx].startModel == sModel && eModel.prevLine[idx].endModel==eModel) {
            eModel.prevLine.splice(idx,1);
            eModel.prevModel.splice(idx,1);
        }
    }
    //eModel.prevModel 수정
    canvas.remove(currentSelectedArrow.triangle);
    canvas.remove(currentSelectedArrow);
    canvas.renderAll();

}

//모델 삭제시에 연결된 Line 모두 제거
function clearLine(model){
    if(model==null) return;
    if(model.nextLine !=null) {
        for(var idx=0 ; idx<model.nextLine.length;idx++){
            console.log(model.nextLine[idx].line);
            currentSelectedArrow = model.nextLine[idx].fabricModel.line;
            deleteLineArrow();
        }
    }
    if(model.prevLine !=null) {
        for(var idx=0 ; idx<model.prevLine.length;idx++){
            currentSelectedArrow = model.prevLine[idx].fabricModel.line;
            deleteLineArrow();
        }
    }
}


/////////////////////////////////////////////
////////////Model Connection/////////////////
/////////////////////////////////////////////
var makingModel = false;
var selectedModel = [];

function modelConnect(model){
    if(!makingModel) return;

    if(selectedModel.length==0){
        selectedModel.push(model);
    }else if(selectedModel.length==1){
        selectedModel.push(model);

        if(selectedModel[0] ==selectedModel[1]){
            //에러
            selectedModel=[];
            makingModel=false;
            connectComplete();
            //alert("같은 모델을 연결할 수 없습니다.");
            return;
        }
        //Make Arrow
        var prevModel = selectedModel[0];
        var nextModel = selectedModel[1];

        var curLine = new LineArrow(prevModel,nextModel);

        if(prevModel.nextLine ==null) prevModel.nextLine=[];
        if(prevModel.nextModel ==null) prevModel.nextModel=[];
        if(nextModel.prevLine ==null) nextModel.prevLine=[];
        if(nextModel.prevModel ==null) nextModel.prevModel=[];

        prevModel.nextLine.push(curLine);
        prevModel.nextModel.push(nextModel);
        nextModel.prevLine.push(curLine);
        nextModel.prevModel.push(prevModel);

        selectedModel=[];
        makingModel=false;
        connectComplete();
    }else{
        //에러
        selectedModel=[];
        makingModel=false;
        connectComplete();
    }
}


function trackingModel(currentModel){
    var nextLine = currentModel.nextLine;
    var prevLine = currentModel.prevLine;

    if(nextLine !=null){
        for(var i=0;i<nextLine.length;i++){
            nextLine[i].changeStartModel(currentModel);
        }
    }
    if(prevLine !=null){
        for(var i=0;i<prevLine.length;i++){
            prevLine[i].changeEndModel(currentModel);
        }
    }
}


function clearConnectModelDelete(){
    $('#connectionDelete').hide();
}

function makeConnectModelDelete(){
    $('#connectionDelete').show();
}
