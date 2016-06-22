require(["nbextensions/widgets/widgets/js/widget",
    "nbextensions/widgets/widgets/js/manager"], function(widget, manager) {
    var CameraView = widget.DOMWidgetView.extend({
        render: function() {
            var that = this;
            that.video  = $('<video>')[0];
            that.canvas = $('<canvas>')[0];
            that.width  = 640;
            that.height = 480;
            that.streaming = false;

            // We append the HTML elements.
            setTimeout(function() {
                that.$el.append(that.video).
                append(that.canvas);
                that.canvas.style.display = 'none';
            }, 200);

            // We initialize the webcam.
            navigator.getMedia = (navigator.getUserMedia       ||
            navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia    ||
            navigator.msGetUserMedia);

            navigator.getMedia({video: true, audio: false},
                function(stream) {
                    if (navigator.mozGetUserMedia) {
                        that.video.mozSrcObject = stream;
                    } else {
                        var vendorURL = window.URL || window.webkitURL;
                        that.video.src = vendorURL.createObjectURL(stream);
                    }
                    that.video.stream = stream;
                    that.video.play();
                },
                function(err) {
                    console.log("An error occured! " + err);
                }
            );

            // We initialize the size of the canvas.
            that.video.addEventListener('canplay', function(ev){
                if (!that.streaming) {
                    that.height = that.video.videoHeight / (that.video.videoWidth / that.width);
                    that.video.setAttribute('width', that.width);
                    that.video.setAttribute('height', that.height);
                    that.canvas.setAttribute('width', that.width);
                    that.canvas.setAttribute('height', that.height);

                    that.streaming = true;
                }
            }, false);

            // It takes a picture and sends it to the model.
            function takepicture() {
                that.canvas.width = that.width;
                that.canvas.height = that.height;

                // We take a screenshot from the webcam feed and
                // we put the image in the first canvas.
                that.canvas.getContext('2d').drawImage(that.video,
                    0, 0,
                    that.width, that.height);

                // We export the canvas image to the model.
                that.model.set('imageurl', that.canvas.toDataURL('image/png'));
                that.touch();
            }

            function destroy() {
                if (that.video) {
                    that.video.stream.getVideoTracks()[0].stop();
                    delete that.video.stream;
                    that.video.remove();
                    delete that.video;
                }
                if (that.canvas) {
                    that.canvas.remove();
                    delete that.canvas;
                }
            }

            window.addEventListener('beforeunload', function(event) {
                destroy();
            });

            that.model.on('change:take_snapshot', takepicture);

            that.on("remove", destroy);
            that.on("comm:dead", destroy);

        }
    });

    // Register the view with the widget manager.
    manager.WidgetManager.register_widget_view('CameraView', CameraView);
});
