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
      console.log(e)
      event = JSON.parse(e.data)

      if(event.event == "add"){
        $scope.$apply(function() {
            $scope.downloading.push(event.data);
        });
        
      }

      if(event.event == "downloaded"){
        $scope.$apply(function() {
            $scope.downloaded.push(event.data);
            for (var i = $scope.downloading.length - 1; i >= 0; i--) {
                if ($scope.downloading[i] == event.data.data.webpage_url) {
                    $scope.downloading.splice(i, 1);
                };
            };
        });
      }
  };

  $scope.add = function() {
    $http.post('/api/downloads', {'url':$scope.url});
    $scope.url = '';
  };

});