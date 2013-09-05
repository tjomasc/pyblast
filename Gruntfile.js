module.exports = function(grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        less: {
            options: {
                paths: ['<%= pkg.resources %>bootstrap-3.0.0/less/', '<%= pkg.name %>/resources/less/*']
            },
            default: {
                files: {
                    "<%= pkg.name %>/static/css/styles.css": "<%= pkg.name %>/static/less/styles.less",
                }
            }
        },
        watch: {
            files: ['<%= pkg.name %>/static/less/*'],
            tasks: ['less'],
        },
    });

    /*
    grunt.event.on('watch', function(action, filepath, target) {
        grunt.log.writeln(target + ': ' + filepath + ' has ' + action);
    });
    */

    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-notify');

    grunt.registerTask('default', ['less']);

};
