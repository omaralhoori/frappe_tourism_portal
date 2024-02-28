/**
 * Zlata Loader
 * tiny javascript library to draw simple loaders on web pages.
 * @author mazurinv@gmail.com
 * web page: http://mazurinv.ru
 * Copyright 2018 Vladimir Mazourin
 */

var ZlataLoader = function (params) {
    if (ZlataLoader.prototype.instances[params.id] !== undefined) {
        ZlataLoader.prototype.instances[params.id].redraw();
        return;
    }
    this.params = Object.create(ZlataLoader.prototype.defaultParams);
    this.properties = Object.create(ZlataLoader.prototype.properties);
    for (var key in params) {
        this.params[key] = params[key];
    }
    if (document.getElementById(params.id) === null) {
        return;
    }
    ZlataLoader.prototype.instances[params.id] = this;
    this.draw()
};
ZlataLoader.prototype.instances = {};
ZlataLoader.prototype.properties = {
    ctx: undefined,
    curr: 0,
    canvasWidth: 0,
    canvasHeight: 0
};
ZlataLoader.prototype.defaultParams = {
    id: 'ZlataLoader',
    radius: 50,
    lineWidth: 1,
    mode: 'picture',
    lineColor: "#fff",
    imageWidth: 64,
    imgSrc: "icon.png",
    speed: -1
};

ZlataLoader.prototype.draw = function() {
    var wrapper = document.getElementById(this.params.id);
    var width = (this.params.radius + this.params.imageWidth) * 2;
    var height = width;
    wrapper.innerHTML = "<canvas id='"+this.params.id+"_canvas'></canvas>";
    this.properties.ctx = document.getElementById(this.params.id+"_canvas").getContext('2d');
    this.properties.canvasWidth = width;
    this.properties.canvasHeight = height;
    document.getElementById(this.params.id+'_canvas').setAttribute("width", this.properties.canvasWidth);
    document.getElementById(this.params.id+'_canvas').setAttribute("height", this.properties.canvasHeight);
    // document.getElementById(this.params.id).style.position = "relative";
    this.properties.img = new Image();
    var that = this;
    this.properties.img.onload = function() {
        that.params.imageRatio = this.width / this.height;
        that.animate();
    };
    this.properties.img.src = this.params.imgSrc;
};

ZlataLoader.prototype.animate = function (draw_to) {
    var ctx = this.properties.ctx;
    if (draw_to !== undefined) {
        ctx.clearRect(0, 0, this.properties.canvasWidth, this.properties.canvasHeight);
    }
    if (this.params.mode === 'double') {
        ctx.beginPath();
        ctx.arc(
            (this.properties.canvasWidth-this.params.lineWidth) / 2,
            (this.properties.canvasWidth-this.params.lineWidth) / 2,
            (this.properties.canvasWidth) / 2 - this.params.imageWidth / 3,
            Math.PI * 30 / 180,
            Math.PI * 150 / 180,
            false
        );
        ctx.fillStyle = 'transparent';
        ctx.fill();
        ctx.lineWidth = this.params.lineWidth;
        ctx.strokeStyle = this.params.lineColor;
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(
            (this.properties.canvasWidth-this.params.lineWidth) / 2,
            (this.properties.canvasWidth-this.params.lineWidth) / 2,
            (this.properties.canvasWidth) / 2 - this.params.imageWidth / 3,
            Math.PI * 210 / 180,
            Math.PI * 330 / 180,
            false
        );
        ctx.fillStyle = 'transparent';
        ctx.fill();
        ctx.lineWidth = this.params.lineWidth;
        ctx.strokeStyle = this.params.lineColor;
        ctx.stroke();
        ctx.drawImage(
            this.properties.img,
            this.properties.canvasWidth - this.params.imageWidth,
            (this.properties.canvasHeight - this.params.imageWidth * this.params.imageRatio) / 2,
            this.params.imageWidth,
            this.params.imageWidth * this.params.imageRatio
        );
        ctx.translate(this.properties.canvasWidth / 2, this.properties.canvasHeight / 2);
        ctx.rotate( Math.PI);
        ctx.translate(- this.properties.canvasWidth / 2, - this.properties.canvasHeight / 2);
        ctx.drawImage(
            this.properties.img,
            this.properties.canvasWidth - this.params.imageWidth,
            (this.properties.canvasHeight - this.params.imageWidth * this.params.imageRatio) / 2,
            this.params.imageWidth,
            this.params.imageWidth * this.params.imageRatio
        );
        ctx.translate(this.properties.canvasWidth / 2, this.properties.canvasHeight / 2);
        ctx.rotate( - Math.PI);
        ctx.translate(- this.properties.canvasWidth / 2, - this.properties.canvasHeight / 2);
    } else if (this.params.mode === 'single') {
        ctx.beginPath();
        ctx.arc(
            (this.properties.canvasWidth-this.params.lineWidth) / 2,
            (this.properties.canvasWidth-this.params.lineWidth) / 2,
            (this.properties.canvasWidth) / 2 - this.params.imageWidth / 3,
            Math.PI * 30 / 180,
            -Math.PI * 30 / 180,
            false
        );
        ctx.fillStyle = 'transparent';
        ctx.fill();
        ctx.lineWidth = this.params.lineWidth;
        ctx.strokeStyle = this.params.lineColor;
        ctx.stroke();
        ctx.drawImage(
            this.properties.img,
            this.properties.canvasWidth - this.params.imageWidth,
            (this.properties.canvasHeight - this.params.imageWidth * this.params.imageRatio) / 2,
            this.params.imageWidth,
            this.params.imageWidth * this.params.imageRatio
        );
    } else {
        ctx.drawImage(
            this.properties.img,
            this.properties.canvasWidth - this.params.imageWidth,
            (this.properties.canvasHeight - this.params.imageWidth * this.params.imageRatio) / 2,
            this.params.imageWidth,
            this.params.imageWidth * this.params.imageRatio
        );
    }
    ctx.translate(this.properties.canvasWidth / 2, this.properties.canvasHeight / 2);
    ctx.rotate(draw_to * Math.PI / 180);
    ctx.translate(- this.properties.canvasWidth / 2, - this.properties.canvasHeight / 2);

    var requestAnimationFrame = window.requestAnimationFrame ||
        window.mozRequestAnimationFrame ||
        window.webkitRequestAnimationFrame ||
        window.msRequestAnimationFrame;
    requestAnimationFrame(function (frameTime) {
        for (var key in ZlataLoader.prototype.instances) {
            var instance = ZlataLoader.prototype.instances[key];
            if (instance.properties.frameTime === frameTime) {
                return;
            }
            instance.properties.frameTime = frameTime;
            instance.animate(instance.params.speed);
        }
    });
};