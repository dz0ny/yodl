;(function(window, Raven, console) {
'use strict';

var originalConsole = console,
    logLevels = ['debug', 'info', 'warn', 'error'],
    level;

var logForGivenLevel = function(level) {
    return function () {
        var args = [].slice.call(arguments);
        Raven.captureMessage('' + args, {level: level, logger: 'console'});

        // this fails for some browsers. :(
        if (originalConsole[level]) {
             originalConsole[level].apply(null, args);
        }
    };
};


level = logLevels.pop();
while(level) {
    console[level] = logForGivenLevel(level);
    level = logLevels.pop();
}
// export
window.console = console;

}(this, Raven, console || {}));


angular.module('yomm', [
    'controllers'
])
angular.module('controllers', [])
.controller('MainCtrl', function($scope, $http) {
  var sock = new WebSocket("ws://"+document.location.host+"/ws");

  function onStatus(data) {
    $scope.downloading = data.downloading;
    $scope.downloaded = data.downloaded;
  };
  
  sock.onopen = function() {
        $http.get('/api/downloads').success(onStatus);
  };

  sock.onmessage = function(e) {
      event = JSON.parse(e.data)
      if(event.event == "add"){
        $scope.$apply(function() {
            $scope.downloading.push(event.data);
        });
        
      }

      if(event.event == "downloaded"){
        $scope.$apply(function() {
            $scope.downloaded.push(event.data);
        });

        for (var i = $scope.downloading.length - 1; i >= 0; i--) {
            if ($scope.downloading[i] == event.data.data.webpage_url) {
                $scope.$apply(function() {
                    $scope.downloading.splice(i, 1);
                });
            };
        };

      }
  };

  $scope.add = function() {
    $http.post('/api/downloads', {'url':$scope.url});
    $scope.url = '';
  };

});