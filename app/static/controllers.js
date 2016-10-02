function showValueSlider(newValue)
{
    document.getElementById("rangeslider").innerHTML=newValue;
}

function showValueSlider2(newValue)
{
    document.getElementById("rangeslider2").innerHTML=newValue;
}

var MilightApp = angular.module('MilightApp',[]);

MilightApp.controller('milightCtrl', function ($scope, $http) {
    $scope.bridge = null;
    $scope.availableBridges = [];

    $http({
            method: 'GET',
            url: '/milight/bridges'
        }).success(function (result) {
        $scope.availableBridges = result.bridges;
    });
});

MilightApp.controller('dropdownCtrl', ['$scope','CustomerService', function($scope, CustomerService) {

  $scope.customer = {
    Bulb:'',
    Action: ''
  };

  $scope.bulbs = CustomerService.getBulb();

  $scope.getBulbActions = function(){
    $scope.actions = CustomerService.getBulbAction($scope.customer.Bulb);
  }


}]);

MilightApp.factory("CustomerService", ['$filter', function($filter){
 var service = {};


  var bulblist = [
            { "id": 1, "bulb": "RGBW" },
            { "id": 2, "bulb": "WHITE" },
    ];

  var actionlist = [
    {"action":"on", "bulbId":1},
    {"action":"off", "bulbId":1},
    {"action":"white", "bulbId":1},
    {"action":"brightness", "bulbId":1},
    {"action":"disco", "bulbId":1},
    {"action":"increase_disco_speed", "bulbId":1},
    {"action":"decrease_disco_speed", "bulbId":1},
    {"action":"color", "bulbId":1},
    {"action":"on", "bulbId": 2},
    {"action":"off", "bulbId": 2},
    {"action":"increase_brightness", "bulbId": 2},
    {"action":"decrease_brightness", "bulbId": 2},
    {"action":"increase_warmth", "bulbId": 2},
    {"action":"decrease_warmth", "bulbId": 2},
    {"action":"brightmode", "bulbId": 2},
    {"action":"nightmode", "bulbId": 2}
  ];

  service.getBulb = function(){
    return bulblist;
  };

  service.getBulbAction = function(bulbId){
    var actions = ($filter('filter')(actionlist, {bulbId: bulbId}));
    return actions;
  };

  return service;

}]);
