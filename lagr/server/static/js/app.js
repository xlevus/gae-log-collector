var app = angular.module("RealTimeApp", ['ngAnimate']);

var LogController = function($scope){
    $scope.logs = {};

    $scope.sort = function(){
        for (key in $scope.logs){
            contents = $scope.logs[key];
            $scope.logs[key] = contents.sort(function(a,b){
                return a.time < b.time;
            });
        }
    }

    var ch = new goog.appengine.Channel(token);
    var sock = ch.open();

    sock.onmessage = function(message){
        var payload = JSON.parse(message.data);
        var app = payload.application;

        if (app in $scope.logs){
            $scope.logs[app].push(payload);
        }
        else{
            $scope.logs[app] = [];
            $scope.logs[app].push(payload);
        }
        console.log("Just pushed " + payload);
        console.log($scope.logs);
        $scope.sort();
        $scope.$apply();
    };

    $scope.socket = sock;

    $scope.columns = [
        {
            name: "time",
            active: true
        },
        {
            name: "level",
            active: true
        },
        {
            name: "message",
            active: true
        },
        {
            name: "module",
            active: false
        },
        {
            name: "filename",
            active: false
        },
        {
            name: "func_name",
            active: false
        }
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