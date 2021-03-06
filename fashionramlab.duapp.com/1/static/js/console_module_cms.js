﻿function add_tag_text(t, txt) {
	$(t).before('<div class="tag"><span>' + txt + '</span><a href="#" onclick="remove_tag(this)">x</a></div>');
	$(t).val('');
}
function add_tag(t) {
	add_tag_text(t, $(t).val());
}
function remove_tag(t) {
	$(t).parent().remove();
}
/*function add_tags(txt) {
	$('#updatags').before('<div class="tag"><span>' + txt + '</span><a href="#" onclick="remove_tag(this)">x</a></div>');
	$('#updatags').val('');
}*/

/*function addconsole_module_cms(){
    var doc = $.parseXML('<article/>');
    var console_module_cmsid=$("#mpid").val();
    $(doc).find("article").attr("mpid",console_module_cmsid);
	function create_node(tag, name) {
		e = doc.createElement(tag);
		e.appendChild(doc.createCDATASection(name));
		return e;
	}
    var oeditor = CKEDITOR.instances.section1.getData();
	doc.documentElement.appendChild(create_node('title', $("#title").val()));
	doc.documentElement.appendChild(create_node('priority', $("#priority").val()));
	doc.documentElement.appendChild(create_node('content', oeditor));
	tags = doc.createElement('tags');
	$(".tag span").each(function(){
		tags.appendChild(create_node('tag', $(this).text()));
	});
	doc.documentElement.appendChild(tags);

	rawxml = new XMLSerializer().serializeToString(doc);
    alert(rawxml)
		 $.ajax({
			    type: 'POST',
			   url: 'mparticle',
			   data:rawxml,
                statusCode:{
                  200:function(){
                      $("#dialog-console_module_cms").dialog( "close" );
                      mparticles_mpid();
                  },500:function(){
                      $("#addcms").text("添加失败");
                  }

              }

			});
}*/

function insert_article(){
    doc = $.parseXML('<article/>');   //根节点
    oeditor = CKEDITOR.instances.section1.getData();   //拿到副文本
    doc.documentElement.appendChild(create_node('priority', $("#priority").val()));// 优先级
    doc.documentElement.appendChild(create_node('title', $("#title").val()));      //标题
    doc.documentElement.appendChild(create_node('summary', $("#summary").val()));  // 概述
    doc.documentElement.appendChild(create_node('thumb', $("#thumb").val()));      //缩略图
    doc.documentElement.appendChild(create_node('enabled', $("#enabled").val()));  //授权
    doc.documentElement.appendChild(create_node('images', $("#images").val()));    //图片路径
    doc.documentElement.appendChild(create_node('content', oeditor));              // 副翁本
    tags = doc.createElement("tags");
    tags.appendChild(create_node('tag', null));
    $(tags).find('tag').attr("id",$("#tags").val());
	doc.documentElement.appendChild(tags);
    xmldocument = new XMLSerializer().serializeToString(doc);   //   生成XML

    $.ajax({
       type: 'POST',
       url: '/mod/cms/mparticle/'+$("#mpid").val(),
       data:xmldocument,
       statusCode:{
          200:function(){
              $("#dialog-console_module_cms").dialog( "close" );
              mparticles_mpid();
          },500:function(){
              $("#addcms").text("添加失败");
          }
       }
    });
    function create_node(tag, name) {
        e = doc.createElement(tag);
        e.appendChild(doc.createCDATASection(name));
        return e;
    }
}

// 查出当前mpid的标签
function find_article_tags(){
     $.ajax({
        type:'GET',
        url: '/mptags/'+ $("#mpid").val(),
        success:function(date){
            $(date).children("tags").children("tag").each(function(){
                  var id = $(this).attr("id");
                  var name = $(this).attr("name");
                  $("#tags").append("<option value ='"+ id +"'>"+ name +"</option>");
                  tagselement(this,0);
            });
        }
    });
}
function tagselement(ele,level){
    $(ele).children("tag").each(function(){
          var id = $(this).attr("id");
          var name = $(this).attr("name");
          var n = '<span style="display:inline-block;width:'+ level*20 + 'px"/>';
          $("#tags").append("<option value ='"+ id +"'>"+n + name +"</option>");
          tagselement(this,level+1);
    })
}
// 查出当前putmpid的标签
function putfind_article_tags(){
     $.ajax({
        type:'GET',
        url: '/mptags/'+ $("#mpid").val(),
        success:function(date){
            $("#updatetag").empty();
            $(date).children("tags").children("tag").each(function(){
                  var id = $(this).attr("id");
                  var name = $(this).attr("name");
                  $("#updatetag").append("<option value ='"+ id +"'>"+ name +"</option>");
                  puttagselement(this,0);
            });
        }
    });
}
function puttagselement(ele,level){
    $(ele).children("tag").each(function(){
          var id = $(this).attr("id");
          var name = $(this).attr("name");
          var n = '<span style="display:inline-block;width:'+ level*20 + 'px"/>';
          $("#updatetag").append("<option value ='"+ id +"'>"+n + name +"</option>");
          puttagselement(this,level+1);
    })
}


//新增资讯
function showconsole_module_cms(){
  if (CKEDITOR.instances['section1']) {
        CKEDITOR.instances['section1'].destroy();
  }
  CKEDITOR.replace('section1');
  CKEDITOR.instances.section1.setData("");
  $("#title").val("");
  $("#imagesShow").text("");
  $("#tag_input").html("");
  $("#addcms").text("");
  find_article_tags();   //预加载所有标签
  $("#dialog-console_module_cms").dialog("open");
  mparticles_mpid();
}

//根据mpid获得概要列表
function mparticles_mpid(){
   $.ajax({
   type:'GET',
   url: '/mod/cms/mparticles/'+ $("#mpid").val(),
   success:function(date){
       $("#body").empty();
       $(date).find("article").each(function(){
          var id = $(this).attr("id");                        //编号
          var priority = $(this).children("priority").text(); //优先级
          var title = $(this).children("title").text();       //标题
          var datetime = $(this).children("dt").text();       //时间
          var summary = $(this).children("summary").text();   //概述
          var thumb =$(this).children("thumb").text();      //缩略图
          var enabled = $(this).children("enabled").text();   //授权
          //  var tags =  $(this).find("tags").children("tag").attr('name'); //标签
          var tags;
          $(this).children("tags").children("tag").each(function(){
             tags= $(this).attr('name')+' ';  //标签
          });

          $("#body").append("<tr id='"+id+"'><td >" + title +"</td>"
             +"<td>" + priority +"</td>"
             +"<td>" + datetime +"</td>"
             +"<td >" + summary +"</td>"
             +"<td>" + thumb +"</td>"
             +"<td>" + enabled +"</td>"
             +"<td>"+ tags +"</td>"
             +"<td><a href='javascript:update_article_cms("+id+")'>编辑</a></td></tr>");
          });

       }
   });
}
function mparticle_id(id){//列出标签为id的信息的详细列表
    $.ajax({
       type:'GET',
       url: '/mod/cms/article/'+ id,
       success:function(date){
           $(date).find("article").each(function(){
              var priority = $(this).children("priority").text(); //优先级
              var title = $(this).children("title").text();       //标题
              var summary = $(this).children("summary").text();   //概述
              var thumb =$(this).children("thumb").text();      //缩略图
              var enabled = $(this).children("enabled").text();   //授权
              var content = $(this).children("content").text();   //详细信息
              var tags ;
              $(this).find("tags").children("tag").each(function(){
                 tags = $(this).attr('name'); //标签
              });
               $("#updatitle").val(title);       //标题
               $("#updatpriority").val(priority);//优先级
               $("#updatesummary").val(summary); //概述
               $("#updatethumb").val(thumb);     //缩略图
               $("#updateenabled").val(enabled); //授权
               CKEDITOR.instances.section2.setData(content); //详细信息
               $("#updatetag").val(tags);        //标签

           });

       }
    });
}




function update_article_cms(id){
    mparticle_id(id);//列出标签为id的信息的详细列表
    putfind_article_tags();
    if (CKEDITOR.instances['section2']) {
        CKEDITOR.instances['section2'].destroy();
    }
    CKEDITOR.replace('section2');
    CKEDITOR.instances.section2.setData("");
    $("#dialog-console_module_update" ).dialog({
        resizable: false,
        height:720,
        width: 600,
        modal: true,
        buttons: {
            "修改": function() {
                update_article(id);
                $("#dialog-console_module_update").dialog("close");
            }
        }
    });

}
function update_article(id){
     var article = $.parseXML('<article/>');
     article.documentElement.appendChild(upcreate_node('title',$("#updatitle").val()));   //标题
     article.documentElement.appendChild(upcreate_node('priority',$("#updatpriority").val()));  //优先级
     article.documentElement.appendChild(upcreate_node('summary', $("#updatesummary").val()));    //概述
     article.documentElement.appendChild(upcreate_node('enabled', $("#updateenabled").val()));    //授权
     article.documentElement.appendChild(upcreate_node('thumb',  $("#updatethumb").val()));      //缩略图
     article.documentElement.appendChild(upcreate_node('content',$("textarea").text()));         //详细信息
     tags = article.createElement("tags");                         //标签
     tags.appendChild(upcreate_node('tag', null));
     $(tags).find('tag').attr("id", $("#updatetag").val());
     images = article.createElement('images');                     //图片
     images.appendChild(upcreate_node('img',null));
     $(images).find('img').attr('src',$('#addsection').val());
     article.documentElement.appendChild(images);
     article.documentElement.appendChild(tags);
     xmldocument = new XMLSerializer().serializeToString(article);
     $.ajax({
        type: 'PUT',
        url: '/mod/cms/article/'+id,
        data:xmldocument,
        statusCode:{
            200:function(){
                mparticles_mpid();
            },500:function(){
                $("#upatacms").text("修改失败");
            }
        }
     });

    function upcreate_node(tag, name) {
    var e = article.createElement(tag);
    e.appendChild(article.createCDATASection(name));
    return e;
}
}



//列出标签为id的信息的详细列表
function findtag(tagid){
           $.ajax({
		   type:'GET',
           url:'/mod/cms/article/'+tagid,
		   success:function(date){
           $("#mparticlelist tr:not(#titlist)").remove();
		   $(date).find("article").each(function(){
                     id = $(this).attr("id");
                     priority = $(this).children("priority").text();
                     dt = $(this).children("dt").text();
		             title = $(this).children("title").text();
				     content = $(this).children("content").text();
				     tags = $(this).children("tags").text();
                     tag="";
                     $(this).children("tags").find("tag").each(function(){
                      tag+="<span>"+$(this).text()+"</span>";
                     });
                     $("#mparticlelist").append("<tr><td data-article-title="+id+">" +title+
					 "</td><td data-article-priority="+id+">" + priority +
                     "</td><tddata-article-priority="+id+">" + dt +
					 "</td><td data-article-content="+id+">" + content +
                     "</td><td data-article-tags="+id+">"+ tag +"</td><td><a href='javascript:update_modole_cms("+id+")'>编辑</a></td></tr>");
				     });
		    	 }
		   });
}



/*
function update_modole_cms(id){
    $(".tag").remove();
    var title=$("#mparticlelist [data-article-title="+id+"]").text();
    var content=$("#mparticlelist [data-article-content="+id+"]").html();
    var priority=$("#mparticlelist [data-article-priority="+id+"]").text();
    $("#mparticlelist [data-article-tags="+id+"] span").each(function(){
         $("#prcetag").before('<div class="tag"><span>' + $(this).text() + '</span><a href="#" onclick="remove_tag(this)" name="deletetag">x</a></div>');

    });
    $("#upatacms").text("");
     $("#sectionShow").text("");
    $("#updatitle").val(title);
    $("#updatpriority").val(priority);
    if (CKEDITOR.instances['section2']) {
    CKEDITOR.instances['section2'].destroy();
    }
   CKEDITOR.replace('section2');
   CKEDITOR.instances.section2.setData(content);
     $("#dialog-console_module_update" ).dialog({
      resizable: false,
      height:720,
	  width: 600,
      modal: true,
      buttons: {
        "修改": function() {
            updateconsole_module_cms(id);
            $("#dialog-console_module_update").dialog("close");
        }
      }
    });
}


function updateconsole_module_cms(id){
var doc = $.parseXML('<article/>');
	function create_node(tag, name) {
		e = doc.createElement(tag);
		e.appendChild(doc.createCDATASection(name));
		return e;
	}
    var oeditor2 = CKEDITOR.instances.section2.getData();
	doc.documentElement.appendChild(create_node('title', $("#updatitle").val()));
	doc.documentElement.appendChild(create_node('priority', $("#updatpriority").val()));
	doc.documentElement.appendChild(create_node('content', oeditor2));
	tags = doc.createElement('tags');
	$(".tag span").each(function(){
		tags.appendChild(create_node('tag', $(this).text()));
	});
	doc.documentElement.appendChild(tags);
	rawxml = new XMLSerializer().serializeToString(doc);
		 $.ajax({
			    type: 'PUT',
			   url: '/mparticle/'+id,
			   data:rawxml,
			  statusCode:{
                  200:function(){
                      mparticles_mpid();
                  },500:function(){
                      $("#upatacms").text("修改失败");
                  }

              }

			});
}*/
//查看图片列表
function findListIamges(){
	$.ajax({
		   type:'GET',
		   url: '/myimg',
		   success:function(date){
           	$("#images option").remove();
		   $(date).find("images").children("image").each(function(){
				    var names = $(this).text();
                    var name = $(this).text();
					var pa = $('<option />');
					pa.text(names);
                    pa.val(name);
				    $("#images").append(pa);

				   });

		    	}
		   });
}
function addsectionListIamges(){
	$.ajax({
		   type:'GET',
		   url: '/myimg',
		   success:function(date){
           	$("#addsection option").remove();
		   $(date).find("images").children("image").each(function(){
				    var names = $(this).text();
                    var namesvalue = $(this).text();
					var pa = $('<option />');
					pa.text(names);
                    pa.val(namesvalue);
				    $("#addsection").append(pa);

				   });

		    	}
		   });
}
function addsection(){
CKEDITOR.instances.section1.insertHtml('<img src='+$("#images").val()+'>')
}
function addsection2(){
CKEDITOR.instances.section2.insertHtml('<img src='+$("#addsection").val()+'>')
}
function ajaxFileUpload(){
		 $.ajaxFileUpload({
		        url: '/upload',
                fileElementId:'file',
			   success: function(data) {
                   var name=dadad;
                     alert($(data).find("image").attr("src"));
                      $("#imagesShow").text("上传成功").css({"color":"red"});
                      findListIamges();
			   },error: function(XMLHttpRequest, textStatus, errorThrown) {
                       $("#imagesShow").text("上传失败").css({"color":"red"});
                    }
			});
}
function ajaxFileUpload2(){
		 $.ajaxFileUpload({
		        url: '/upload',
                fileElementId:'sectionImage',
			   success: function(data) {
                      $("#sectionShow").text("上传成功").css({"color":"red"});
                      findListIamges();
			   },error: function(XMLHttpRequest, textStatus, errorThrown) {
                       $("#sectionShow").text("上传失败").css({"color":"red"});
                    }
			});
}