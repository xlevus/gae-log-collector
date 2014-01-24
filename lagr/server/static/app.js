var app = angular.module("RealTimeApp", []);

var HTTPService = function($http){
    var factory = {};

    factory.start = function(){
        var ch = new goog.appengine.Channel("{{ token }}");
        var sock = ch.open();

        sock.onopen = function(){
        };

        sock.onmessage = function(message){
            console.log(message);
        };

        sock.onerror = function(err){
        };

        return sock;
    };
    return factory;
}

app.factory("http_service", HTTPService);

var LogController = function($scope, http_service){
    $scope.logs = http_service.start();
    $scope.columns = [
        {
            name: "Level",
            active: true
        },
        {
            name: "Module",
            active: true
        },
        {
            name: "Message",
            active: true
        },
        {
            name: "Traceback",
            active: true
        },
    ];

    $scope.has_logs = function(){
        if ($scope.logs.length !== 0){
            return true;
        }
        else{
            return false;
        }
    }

    $scope.get_from_content = function(field, info){
        return info[field];
    }

    $scope.filter = function(column){
        var index = $scope.columns.indexOf(column);
        if (index !== -1){
            $scope.columns[index].active = !$scope.columns[index].active;
        }
    }

    $scope.get_class = function(column){
        if (column.active === true){
            return "btn btn-success";
        }
        else{
            return "btn btn-warning";
        }
    }

    $scope.normalize = function(item){
        return item.replace(" ", "_");
    }

    $scope.get_id = function(item){
        console.log("Returning " + "#" + $scope.normalize(item));

        return "#" + $scope.normalize(item);
    }
}

app.controller("logController", LogController);