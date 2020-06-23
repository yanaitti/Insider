var timeout = 1000;
var timer = '';

$(function() {
  var gId = '';
  var cId = '';
  $('#entry').show();

  // Create Game
  $('#createGame').click(function() {
    $('#message').empty();
    $.ajax('create' + '/' + $('#cName_inp').val(),
      {
        type: 'get',
      }
    )
    .done(function(data) {
      $('#gId').text(data);
      $('#cId').text(data);
      $('#cName').text($('#cName_inp').val());
      $('#gStatus').text('waiting');
      gId = data;
      cId = data;
      $('#sec1').show();
      timer = setTimeout(status_check(gId, cId), timeout)
    })
    .fail(function() {
      $('#message').text('エラーが発生しました');
    });
  });

  // Join Game
  $('#joinGame').click(function() {
    $('#message').empty();
    $.ajax($('#gId_inp').val() + '/join/' + $('#cName_inp').val(),
      {
        type: 'get',
      }
    )
    .done(function(data) {
      _tmp = data.split(' ,');
      $('#cId').text(_tmp[0]);
      $('#cName').text(_tmp[1]);
      $('#gStatus').text(_tmp[2]);
      gId = $('#gId_inp').val();
      cId = _tmp[0];
      timer = setTimeout(status_check(gId, cId), timeout)
    })
    .fail(function() {
      $('#message').text('エラーが発生しました');
    });
  });

  // Start Game
  $('#startGame').click(function() {
    $('#message').empty();
    $.getJSON(gId + '/start',
      {
        type: 'get',
      }
    )
    .done(function(data) {
      $('#results').empty();
    })
    .fail(function() {
      $('#message').text('エラーが発生しました');
    });
  });

  // Vote
  $('#vote').click(function() {
    $('#message').empty();
    // put your card
    $.ajax(gId + '/vote/' + $('[name="votelists"] option:selected').val(),
      {
        type: 'get',
      }
    )
    .done(function(data) {
      $('#message').text(data);
    })
    .fail(function() {
      $('#message').text('エラーが発生しました');
    });
  });

  // result
  $('#result').click(function() {
    $('#message').empty();
    $.ajax(gId + '/results',
      {
        type: 'get',
      }
    )
    .done(function(data) {
    })
    .fail(function() {
      $('#message').text('エラーが発生しました');
    });
  });
});

var status_check = function(gId, cId){
  setTimeout(function(){
    $('#message').empty();
    // all status
    $.getJSON(gId + '/status',
      {
        type: 'get',
      }
    )
    .done(function(data) {
      console.log(data)
      $('#gStatus').text(data.status);
      playerPos = 0;

      // Applying List
      $('#applyingList').empty();
      for(var pIdx in data.players){
        // console.log(data.players[pIdx])
        $('#applyingList').append(data.players[pIdx].nickname + '(' + data.players[pIdx].playerid + ')' + ',');
        if(cId == data.players[pIdx].playerid){
          playerPos = pIdx;
        }
      }

      switch(data.status){
        case 'started':
          $('#sec2').show()
          $('#entry').hide();

          $('#yourRole').empty();
          $('#answer').empty();
          if(data.master.playerid == cId){
            $('#yourRole').text('MASTER');
            $('#answer').text('answer: ' + data.answer);
          }else if(data.insider.playerid == cId){
              $('#yourRole').text('INSIDER');
              $('#answer').text('answer: ' + data.answer);
          }else{
            $('#yourRole').text('COMMONS');
          }

          if(jQuery.trim($('#votelists').text()) == ''){
            for(var pIdx in data.votelist){
              $('#votelists').append('<option value="'+data.votelist[pIdx].playerid+'">'+data.votelist[pIdx].nickname+'</option>');
            }
          }

          votedlist = data.votedlist;
          console.log(votedlist.length);
          players = data.players;
          console.log(players.length);
          if(votedlists.length == players.length){
            $('#votedlists').text('aa');
          }
          break;
        case 'end':
          $('#results').empty();
          for(var rIdx in data.results){
            $('#results').append(data.results[rIdx].nickname + ':' + data.results[rIdx].vote);
            if (data.results[rIdx].playerid == data.insider.playerid){
              $('#results').append('&nbsp;INSIDER!!');
            }
            $('#results').append('<br/>');
          }
          $('#votelists').empty();
          break;
      }
    })
    .fail(function() {
      $('#message').text('エラーが発生しました');
    });
    timer = setTimeout(status_check(gId, cId), timeout)
  }, timeout);
}
