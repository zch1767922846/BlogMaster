layui.use(['table', 'layer'], function () {
    var table = layui.table;
    var layer = layui.layer;

    table.render({
        elem: "#pages-table",
        url: "/admin/pages", //数据接口
        method: "get",
        cols: [[
            //表头
            {field: "page_id", title: "ID", width: '10%', sort: true},
            {field: "page_title", title: "标题", width: '15%'},
            {field: "page_category", title: "分类", width: '10%'},
            {field: "page_author", title: "作者", width: '10%'},
            {field: "page_tag", title: "标签"},
            {field: "page_status", title: "状态"},
            {field: "page_publishtime", title: "发布时间"},
            {field: "page_updatetime", title: "更新时间"},
            {field: 'operation', title: '操作', toolbar: '#toolbar-page', width: '10%'}
        ]],
        toolbar: '#toolbar-pages',
        // skin: 'line', //表格风格 line （行边框风格）row （列边框风格）nob （无边框风格）
        even: true,   //隔行换色
        page: true, //开启分页
        limits: [30, 50],  //每页条数的选择项，默认：[10,20,30,40,50,60,70,80,90]。
        limit: 30, //每页默认显示的数量
        parseData: function (res) {
            //res 即为原始返回的数据
            console.log(res)
            return {
                code: res.code, //解析接口状态
                msg: res.message, //解析提示文本
                count: res.count, //解析数据长度
                data: res.data, //解析数据列表
            };
        },
        // 设置响应数据字段名称
        response: {
            statusCode: 20000000, //规定成功的状态码，默认：0
            msgName: "message", //规定状态信息的字段名称，默认：msg
            dataName: "data", //规定数据列表的字段名称，默认：data
        },
        page: true, //开启分页

    });

    //监听行工具事件
    table.on('tool(filter-page-table)', function (obj) {
        var data = obj.data;
        if (obj.event === 'del') {
            layer.confirm('确定删除？', function (index) {
                $.ajax({
                    url: '/page/' + data.id,
                    method: 'Delete',
                    dataType: 'JSON',
                    success: function (result) {
                        console.log(result)
                        if (result.code === 20003002) {
                            obj.del();
                            layer.close(index);
                            layer.msg(result.msg, {icon: 6});
                        } else {
                            layer.msg(result.msg, {icon: 5});
                        }
                    }
                })
            });
        } else if (obj.event === 'edit') {
            layer.open({
                type: 2,
                title: ['更新分类', 'font-size:1.125rem;'],
                skin: 'layui-layer-molv',
                area: ['50%', '50%'],
                icon: 1,
                content: '/admin/page/' + data.id,
                closeBtn: 1,
                shade: 0.2,
                resize: false,
            }, function (value, index) {
                obj.update({
                    email: value
                });
                layer.close(index);
            });
        }
    });

});
