/**
 * Created by koohanmo on 2016. 9. 16..
 */
var canvas = new fabric.Canvas('canvas');
canvas.selection=false;
var canvasX=0;
var canvasY=0;
canvas.on('mouse:move', function(options) {
    canvasX=options.e.clientX;
    canvasY=options.e.clientY;
    //console.log(canvasX,canvasY);
});


/////////////////////////////////////////////
////////////manage ML models/////////////////
/////////////////////////////////////////////
var modelCnt=0;
var models=[];
var currentSelectedArrow;
var currentSelectedModel; // Use when I change options

function getModelById(id){
    for(model in models){
        if(models[model].ID ===id) return models[model];
    }
    return null;
}
function getModelIdxById(id){
    for(model in models){
        if(models[model].ID ===id) return model;
    }
    return null;
}

/////////////////////////////////////////////
/////////Canvas fit to Window////////////////
/////////////////////////////////////////////
function canvaResize (event) {
    var canvasConiner = document.getElementById('canvasContaianer');
    var mid = document.getElementById('mid');
    var head = document.getElementById('nav_head');
    var foot = document.getElementById('nav_footer')
    canvas.setWidth(canvasConiner.clientWidth);
    canvas.setHeight(mid.clientHeight-head.clientHeight-foot.clientHeight);
    canvas.calcOffset();
}

window.onresize = canvaResize;
canvaResize();
canvas.renderAll();