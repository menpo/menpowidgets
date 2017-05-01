requirejs.undef('camera');

define('camera', ["jupyter-js-widgets"], function(widgets) {
    var CameraView = widgets.DOMWidgetView.extend({
        _take_snapshot: function() {
            this.canvas.getContext('2d').drawImage(
                this.video, 0, 0, this.width, this.height);

            this.model.set('imageurl', this.canvas.toDataURL('image/png'));
            this.touch();
        },
        _destroy_video: function() {
            if (this.video) {
                this.video.stream.getVideoTracks()[0].stop();
                delete this.video.stream;
                this.video.remove();
                delete this.video;
            }
            if (this.canvas) {
                this.canvas.remove();
                delete this.canvas;
            }
        },
        _resize_video: function() {
            this.width  = this.model.get('canvas_width');
            this.height = this.video.videoHeight / (this.video.videoWidth / this.width);
            this.video.setAttribute('width', this.width);
            this.video.setAttribute('height', this.height);
            this.canvas.setAttribute('width', this.width);
            this.canvas.setAttribute('height', this.height);
            this.model.set('canvas_height', this.height);
            this.touch();
        },
        _wire_handlers: function() {
            var that = this;
            window.addEventListener('beforeunload', function(_) {
                that._destroy_video();
            });

            that.on("remove", that._destroy_video, that);
            that.on("comm:dead", that._destroy_video, that);
            that.model.on('change:take_snapshot', that._take_snapshot, that);
            that.model.on('change:canvas_width', that._resize_video, that);
        },
        _attach_dom_elements: function() {
            this.$el.append(this.video).append(this.canvas);
            this.canvas.style.display = 'none';
        },
        _attach_error_dom_elements: function(err) {
            var err_dom = document.createElement('div');
            err_dom.innerHTML = "An error has occurred, your browser does not appear " +
                                "to support the HTML5 getUserMedia API. The " +
                                "following error was thrown: <br/>" + err;
            err_dom.style.width = '300px';
            err_dom.style.textAlign = 'center';
            this.$el.append(err_dom);
        },
        render: function() {
            var that = this;
            that.video  = $('<video>')[0];
            that.canvas = $('<canvas>')[0];
            that.width  = that.model.get('canvas_width');
            // Default value, will be overridden
            that.height = 0;
            that.streaming = false;

            // Set video constraints (resolution)
            var video_constraints = true;
            if (that.model.get('hd')) {
                video_constraints = {
                    mandatory: {
                        minWidth: 1280,
                        minHeight: 720
                    }
                };
            }

            // Initialize the webcam
            navigator.getMedia = navigator.getUserMedia       ||
                                 navigator.webkitGetUserMedia ||
                                 navigator.mozGetUserMedia    ||
                                 navigator.msGetUserMedia;

            if (navigator.getMedia !== undefined) {
                navigator.getMedia({video: video_constraints, audio: false},
                    function (stream) { // Success
                        // Add the video/hidden canvas to the DOM
                        that._attach_dom_elements();

                        // Create the stream and display it
                        if (navigator.mozGetUserMedia) {
                            that.video.mozSrcObject = stream;
                        } else {
                            var vendorURL = window.URL || window.webkitURL;
                            that.video.src = vendorURL.createObjectURL(stream);
                        }
                        that.video.stream = stream;
                        that.video.play();

                        // When the video is ready resize it.
                        that.video.addEventListener('canplay', function (_) {
                            if (!that.streaming) {
                                that._resize_video();
                                that.streaming = true;
                            }
                        }, false);

                        // Wire up event handlers
                        that._wire_handlers();
                    },
                    function (err) {  // Error
                        console.log("CameraView ERROR: " + err);
                        that._attach_error_dom_elements(err);
                    }
                );
            } else {
                var err = 'getUserMedia === undefined';
                console.log("CameraView ERROR: " + err);
                that._attach_error_dom_elements(err);
            }
        }
    });

    return {
        CameraView : CameraView
    };
});
