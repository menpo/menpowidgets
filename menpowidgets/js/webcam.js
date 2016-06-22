require(["nbextensions/widgets/widgets/js/widget", "nbextensions/widgets/widgets/js/manager"],
    function(widget, manager) {
    var CameraView = widget.DOMWidgetView.extend({
        render: function() {
            var that = this;
            that.video  = $('<video>')[0];
            that.canvas = $('<canvas>')[0];
            that.width  = that.model.get('canvas_width');
            that.height = 480;
            that.streaming = false;

            // Set video constraints (resolution)
            var video_constraints  = true;
            if (that.model.get('hd')) {
                video_constraints  = {mandatory: {minWidth: 1280, minHeight: 720}};
            }

            // Append the HTML elements
            setTimeout(function() {
                that.$el.append(that.video).append(that.canvas);
                that.canvas.style.display = 'none';
            }, 200);

            // Initialize the webcam
            navigator.getMedia = (navigator.getUserMedia ||
            navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia ||
            navigator.msGetUserMedia);

            navigator.getMedia({video: video_constraints, audio: false},
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
                    that.model.set('error_occurred', true);
                }
            );

            // Resize video
            function resize() {
                that.width  = that.model.get('canvas_width');
                that.height = that.video.videoHeight / (that.video.videoWidth / that.width);
                that.video.setAttribute('width', that.width);
                that.video.setAttribute('height', that.height);
                that.canvas.setAttribute('width', that.width);
                that.canvas.setAttribute('height', that.height);
            }

            // Initialize the size of the canvas
            that.video.addEventListener('canplay', function(ev){
                if (!that.streaming) {
                    resize();
                    that.streaming = true;
                }
            }, false);

            // It takes a picture and sends it to the model
            function takepicture() {
                that.canvas.width = that.width;
                that.canvas.height = that.height;

                // Take a screenshot from the webcam feed and put the image in the canvas
                that.canvas.getContext('2d').drawImage(that.video, 0, 0,
                    that.width, that.height);

                // Export the canvas image to the model
                that.model.set('imageurl', that.canvas.toDataURL('image/png'));
                that.touch();
            }

            // Destroy the webcam
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

            // Add listeners
            window.addEventListener('beforeunload', function(event) {
                destroy();
            });
            that.model.on('change:take_snapshot', takepicture);
            that.on("remove", destroy);
            that.on("comm:dead", destroy);
            that.model.on('change:canvas_width', resize);
        }
    });

    // Register the view with the widget manager
    manager.WidgetManager.register_widget_view('CameraView', CameraView);
});
