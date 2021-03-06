/**
 * Created by TsukiHiBoshi on 14-1-8.
 */
function findListTag(){
    $.ajax({
        type:'GET',
        url: '/mptags/'+ $("#mpid").val(),
        success:function(date){
           arrfun(date);
        }
    });
}

function arrfun(date){
   $(date).find("tags").each(function(){
        /*  var id = $(this).attr("id");
          var name = $(this).attr("name");
          addelement(name,id);*/
          element(this,0);
  });
}
function element(ele,level){
    $(ele).children("tag").each(function(){
          var id = $(this).attr("id");
          var name = $(this).attr("name");
          var n = '<span style="display:inline-block;width:'+ level*50 + 'px"/>';
          addelement(n + name,id);
          element(this,level+1);
    })
}

// 动态添加节点
function addelement(uname, uid){
   $("#body").append("<tr class="+ uid +"><td>" + uname +"</td>"
  // +"<td><button type='button' class='btn' onclick='add_tag("+ uid +")'> 添加标签 </button> &nbsp;&nbsp;<a href='javascript:deleteShowtag("+uid+")'> 删除 </a> &nbsp;&nbsp; <a href='javascript:updateShowdilog("+uid+")'> 修改 </a></td></tr>")
     +"<td><a href='javascript:add_tag("+ uid +")'> 添加标签 </a> &nbsp;&nbsp;<a href='javascript:deleteShowtag("+uid+")'> 删除 </a> &nbsp;&nbsp; <a href='javascript:updateShowdilog("+uid+")'> 修改 </a></td></tr>")

}

// 添加标签弹出窗
function add_tag(id){
     $("#dialog-mp_tog_add").dialog({
          resizable: false,
          height:220,
          width: 600,
          modal: true,
          buttons: {
              "添加": function() {
                   submit_add_tag(id);
                   $(this).dialog( "close" );    //关闭对话框
                   $("#body").empty();
                   findListTag();   // 查出全部标签
              }
          }
      });
}
//  添加标签
function submit_add_tag(id){
    var name = $("#tag_name").val();
    $.ajax({
        type:'POST',
        url: '/tag/'+id,
        data:'<tag  name="'+ name +'"/>',
        statusCode:{
              200:function(){
                  $("#tag_name").val("");
                  $("#addtag").text("");
                  $("#body").empty();
                  findListTag();   // 查出全部标签
                  $("#dialog-mp_tog_add").dialog( "close" );    //关闭对话框
              },500:function(){
                  $("#addtag").text("添加失败");
              }
        }
    });
}
// 添加顶层标签弹出窗
function add_up_tag(){
    $("#dialog-up_tog_add").dialog({
         resizable: false,
         height:220,
         width: 600,
         modal: true,
         buttons: {
             "添加": function() {
                  submit_up_tag();
                  $("#body").empty();
                  findListTag();   // 查出全部标签
                  $(this).dialog( "close" );    //关闭对话框
             }
         }
     });
}
 // 添加顶层标签
function submit_up_tag(){
    var name = $("#up_tag_name").val();
    $.ajax({
        type:'POST',
        url: '/mptag/'+ $("#mpid").val(),
        data:'<tag  name ="'+ name +'"/>',
        statusCode:{
              200:function(){
                  $("#up_tag_name").val("");
                  $("#body").empty();
                  findListTag();   // 查出全部标签
                  $("#dialog-up_tog_add").dialog( "close" );    //关闭对话框
              },500:function(){
                  $("#adduptag").text("添加失败");
              }
        }
    });
}

// 删除标签
function deleteShowtag(id){
    if (confirm("您确定要删除标签嘛？")){
        $.ajax({
            type:'DELETE',
            url: '/tag/'+id,
            statusCode:{
                  200:function(){
                      $("#body").empty();
                      findListTag();   // 查出全部标签
                  },500:function(){
                     alert("删除失败!");
                  }
            }
        });
    }else{
        return
    }
}
// 更新标签
function updateShowdilog(id){
    var uname = $('tr.'+id+' td:eq(0)').text();
     $("#put_tag_name").val(uname);
      $("#dialog-mp_tog_update").dialog({
          resizable: false,
          height:220,
          width: 600,
          modal: true,
          buttons: {
              "更新": function() {
                   updateShowtag(id);
                   $(this).dialog( "close" );    //关闭对话框
                   $("#body").empty();
                   findListTag();   // 查出全部标签
              }
          }
      });
}
function updateShowtag(id){
    var name = $("#put_tag_name").val();
     $.ajax({
            type:'PUT',
            url: '/tag/'+id,
            data: '<tag  name ="'+ name +'"/>',
            statusCode:{
                  200:function(){
                      $("#put_tag_name").val("");
                      $("#body").empty();
                      findListTag();   // 查出全部标签
                      $("#dialog-mp_tog_update").dialog( "close" );    //关闭对话框
                  },500:function(){
                      $("#updatetag").text("修改失败!");
                  }
            }
     });
}