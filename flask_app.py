import io
import base64
import json
import plotly.graph_objects as go
import datetime
import dash_daq as daq

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import numpy as np
import pandas as pd
import dateutil
import plotly.express as px

import flask

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

app.config.suppress_callback_exceptions = True


def get_df(df):
    df_by_day = df.groupby(['报道时间', '省份']).agg({'确诊': np.sum, '出院': np.sum, '死亡': np.sum}) \
        .fillna(0).astype(int)
    df_cum = df_by_day.groupby('省份').cumsum()
    return df_by_day, df_cum


def get_fig(df, title):
    df = df.reset_index()
    df = df[df['报道时间'] >= dateutil.parser.parse('2020-01-18')]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df['报道时间'],
            y=df['确诊'],
            yaxis='y',
            name='确诊',
            text=df['确诊'],
            textposition='auto',
            hovertemplate='%{text}',
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df['报道时间'],
            y=df['死亡'],
            yaxis='y2',
            name='死亡',
            text=df['死亡'],
            textposition='middle right',
            mode='lines+markers',
            hovertemplate='%{text}',
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df['报道时间'],
            y=df['出院'],
            yaxis='y2',
            name='出院',
            text=df['出院'],
            textposition='middle right',
            mode='lines+markers',
            hovertemplate='%{text}',
        )
    )
    fig.update_layout(
        title=title,
        yaxis=dict(
            title='确诊人数',
            titlefont=dict(
                color="#1f77b4"
            ),
            tickfont=dict(
                color="#1f77b4"
            )
        ),

        xaxis_tickformat='%m-%d',
        hovermode='x',
        yaxis2=dict(
            title='死亡\出院人数',
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=0.9725
        )
    )

    return fig


def get_pro_sum(df):
    df = df.reset_index()
    print(df)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df['省份'],
            y=df['确诊'],
            yaxis='y',
            name='确诊',
            text=df['确诊'],
            textposition='auto',
            hovertemplate='%{text}',
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df['省份'],
            y=df['出院'],
            yaxis='y2',
            name='出院',
            text=df['出院'],
            textposition='middle right',
            mode='lines+markers',
            hovertemplate='%{text}',
        )
    )
    fig.update_layout(
        title='各地区累计',
        yaxis=dict(
            title='确诊人数',
            titlefont=dict(
                color="#1f77b4"
            ),
            tickfont=dict(
                color="#1f77b4"
            )
        ),
        hovermode='x',
        yaxis2=dict(
            title='出院人数',
            titlefont=dict(
                color="#00CC66"
            ),
            tickfont=dict(
                color="#00CC66"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=0.9725
        )
    )

    return fig


data = pd.read_excel(r'./static/全国疫情数据.xlsx')
province_list = ['湖北', '海南', '广东', '天津', '辽宁', '香港', '黑龙江', '广西', '浙江', '北京', '云南', '山东', '重庆',
                 '湖南', '上海', '四川', '福建', '青海', '内蒙古', '陕西', '宁夏', '江西', '江苏', '新疆', '贵州', '河南',
                 '吉林', '安徽', '河北', '山西', '甘肃', '澳门', '西藏', '台湾']

data_china = data.loc[data['省份'].isin(province_list), :]
data_china[data_china['省份'] != '湖北']['标签'] = '其他省份'
data_china[data_china['省份'] == '湖北']['标签'] = '湖北'
data_other = data_china[data_china['省份'] != '湖北']

data_china_all = data_china.groupby(['报道时间']).agg({'确诊': np.sum, '出院': np.sum, '死亡': np.sum}) \
    .fillna(0).astype(int)
data_china_all_cum = data_china_all.cumsum()

data_other_day = data_other.groupby(['报道时间']).agg({'确诊': np.sum, '出院': np.sum, '死亡': np.sum}) \
    .fillna(0).astype(int)
data_other_cum = data_other_day.cumsum()

data_city = data_china.groupby(['省份', '城市']).agg({'确诊': np.sum, '出院': np.sum, '死亡': np.sum}) \
    .fillna(0).astype(int)
data_city.sort_values(by=['确诊'], ascending=False, inplace=True)
data_city = data_city.reset_index()


def get_sum(pro):
    df = data_city.groupby('省份').agg({'确诊': np.sum})
    return df.loc[pro, '确诊']


data_city['合计'] = data_city['省份'].apply(lambda x: data_city.groupby('省份').agg({'确诊': np.sum}).loc[x, '确诊'])
fig_px_hubei = px.bar(data_frame=data_city.query('省份 == "湖北"'), x='城市', y='确诊', color='死亡')
fig_px_hubei.update_layout(
    title='湖北各地区累计确诊及死亡数',
    hovermode='x'
)
fig_px_other = px.bar(data_frame=data_city.query('省份 != "湖北"'),
                      x='省份', y='确诊',
                      color='死亡',
                      hover_data=['合计', '城市'])
fig_px_other.update_layout(
    title='其他省市累计确诊数',
    showlegend=False,
)
data_hubei = data.loc[data['省份'] == '湖北', :]

df_china_by_day, df_china_cum = get_df(data_china)
df_hubei_by_day, df_hubei_cum = get_df(data_hubei)

df_china_day_unstack = df_china_by_day.unstack().fillna(0).astype(int)
df_china_cum_unstack = df_china_cum.unstack().fillna(0).astype(int)

df = df_china_by_day.reset_index()
df = df[df['省份'] != '湖北']
fig_pro = px.scatter(df, y='报道时间', x='省份', size='确诊', color='死亡',
                     ) \
    .update_layout(
    title='各地区(非湖北)各日确认病例数',
    yaxis_tickformat='%m-%d'
)

page_2019 = html.Div([
    html.Title('2019-ncov疫情历史数据'),
    html.Div(
        className='2019_content',
        children=[
            html.H3('2019-ncov历史数据汇总',
                    style={'text-align': 'center'}),
            html.A('数据来源：澎湃新闻美数课整理',
                   href='https://shimo.im/sheets/tyWrrrqppYVwQtCW/gVSL1',
                   target='blank',
                   style={'margin-left': '65%'}
                   ),
            html.Div(
                className='new_content',
                children=[
                    html.Div(
                        id='container',
                        className='columns',
                        children=[
                            dcc.Graph(
                                figure=get_fig(
                                    data_china_all,
                                    title='全国每日数据'),
                                className='six columns'
                            ),
                            dcc.Graph(
                                figure=get_fig(
                                    data_china_all_cum,
                                    title='全国累计数据汇总'),
                                className='six columns'),
                            dcc.Graph(
                                figure=get_fig(
                                    df_hubei_by_day,
                                    title='湖北地区每日数据'),
                                className='six columns'),
                            dcc.Graph(
                                figure=get_fig(
                                    df_hubei_cum,
                                    title='湖北地区累计数据'),
                                className='six columns'),
                            html.Span('注：湖北1月23日数据被报道时间稀释，即新闻数据归到其他日期，总数据不变，谅解',
                                      className='twelve columns'),
                            html.Span('注：不考虑时间推移的影响，仅看当前累计数据，总体死亡率略高于2%， 湖北地区接近3%'
                                      '其他地区则明显低些。',
                                      className='twelve columns'),
                            dcc.Graph(
                                figure=get_fig(
                                    data_other_day,
                                    title='湖北外-各地区每日数据'),
                                className='six columns'),
                            dcc.Graph(
                                figure=get_fig(
                                    data_other_cum,
                                    title='湖北外-各地区累计数据'),
                                className='six columns'),
                            html.Span('注：全国数据增长被湖北数据主导，去除湖北省数据，其他省份 ’单日确认增长‘在1-30之后无明显的增长，'
                                      '处于平台波动期，且其他省份死亡案例较少，未来一段时间，湖北省在试剂大量测试后，确认案例'
                                      '可能仍有增长',
                                      className='twelve columns'),
                            dcc.Graph(
                                figure=fig_pro,
                                className='twelve columns'
                            ),
                            dcc.Graph(
                                # figure=get_pro_sum(data_other_pro),
                                figure=fig_px_hubei,
                                className='twelve columns'
                            ),
                            dcc.Graph(
                                # figure=get_pro_sum(data_other_pro),
                                figure=fig_px_other,
                                className='twelve columns'
                            ),
                            html.Span('注：广东、河南、浙江、安徽、江西、湖南几个省份确认案例较多，其他省份与湖北相比较，'
                                      '死亡数量\比率明显偏低。其他省份以防止聚集性传播为主，不必惶恐.'
                                      '湖北地区救助重症患者、控制疫情传播'
                                      '仍有一段路要走。',
                                      className='twelve columns'),
                            html.Span('盼着疫情早日过去，也同样，希望各位珍惜和身边人待在一起的时间。',
                                      className='twelve columns'),
                            html.Span('祝好',
                                      className='twelve columns'),

                        ]),

                ]
            )
        ]
    )
])

index_page = html.Div([
    html.Title('Phebi数据分析'),
    html.Header(html.Meta(name="referrer", content="no-referrer")),
    html.Div(
        id='row_1',
        style={'display': 'flex'},
        children=[
            html.Div(
                id='上传数据',
                className='left_bar',
                children=[
                    html.Div(
                        id='数据上传区域', className='columns',
                        children=[
                            html.H6('数据源'),
                            html.Div(
                                id='all_file_store',
                                hidden=False,
                                className='twelve columns',
                                children=[
                                    dcc.Upload(
                                        id='stock_file',
                                        children=html.Div([
                                            html.A('选择库存文件')]),
                                        className='my_upload',
                                        multiple=False),
                                    dcc.Upload(
                                        id='daily_file',
                                        children=html.Div([
                                            html.A('选择日常数据文件')]),
                                        className='my_upload',
                                        multiple=False),
                                    dcc.Upload(
                                        id='ad_file',
                                        children=html.Div([
                                            html.A('选择广告数据文件')]),
                                        className='my_upload',
                                        multiple=False
                                    ),
                                    dcc.Upload(
                                        id='property_file',
                                        children=html.Div([
                                            html.A('选择产品属性文件')]),
                                        className='my_upload',
                                        multiple=False),
                                    html.Div([
                                        html.P('演示', className='four columns'),
                                        daq.BooleanSwitch(
                                            id='choose_demo',
                                            on=False),
                                    ],
                                        className='six columns'

                                    ),
                                ]
                            ),
                        ]),
                    html.Div(id='数据存储区域',
                             children=[
                                 dcc.Store(id='daily_file_store', storage_type='session'),
                                 dcc.Store(id='daily_filename_store', storage_type='session'),
                                 dcc.Store(id='ad_file_store', storage_type='session'),
                                 dcc.Store(id='ad_filename_store', storage_type='session'),
                                 dcc.Store(id='output_store', storage_type='session'),
                                 html.Tbody([
                                     html.Th('文件内容'),
                                     html.Th('文件名'),
                                     html.Tr([
                                         html.Td(id='daily_file_td'),
                                         html.Td(id='daily_filename_td'),
                                     ]),
                                     html.Tr([
                                         html.Td(id='ad_file_td'),
                                         html.Td(id='ad_filename_td'),
                                     ])
                                 ],
                                 ),

                             ]),
                ]),
            html.Div(id='聚合数据展示区域',
                     className='top_bar',
                     children=[
                         html.Div(id='daily_graph_ploy'),
                         html.H5('聚合数据区域'),
                         html.P('数据汇总、完成度等等')
                     ]),
        ]),
    html.Div(
        id='row_2',
        className='content_page',
        children=[
            html.Div(
                className='columns',
                children=[
                    html.Div(
                        draggable='true',
                        id='ASIN选择',
                        className='columns',
                        style={'position': 'fixed', 'left': '2.5%', 'top': '75%', 'width': '400px'},
                        children=[
                            html.Div(
                                className='four columns',
                                children=[
                                    dcc.Dropdown(id='select_cate_one',
                                                 style={'width': '120px'},
                                                 placeholder="一级类目", ),
                                    dcc.Dropdown(id='select_cate_two',
                                                 style={'width': '120px'},
                                                 placeholder="二级类目", ),
                                    dcc.Dropdown(id='select_fsku',
                                                 style={'width': '120px'},
                                                 placeholder="父sku", ),
                                    dcc.Dropdown(id='select_sku',
                                                 style={'width': '120px'},
                                                 placeholder="sku", ),
                                ],
                            ),
                            html.Div(
                                className='eight columns',
                                children=[
                                    dcc.Dropdown(id='select_ad_comb',
                                                 style={'width': '175px'},
                                                 placeholder='广告组合'),
                                    dcc.Dropdown(id='select_ad_action',
                                                 style={'width': '175px'},
                                                 placeholder="广告活动", ),
                                    dcc.Dropdown(id='select_ad_group',
                                                 style={'width': '175px'},
                                                 placeholder="广告组", ),
                                    dcc.Dropdown(id='select_ad_words',
                                                 style={'width': '175px'},
                                                 placeholder="广告投放", ),
                                ]
                            ),
                        ]),
                    html.Div(
                        id='pic_bar',
                        style={'position': 'fixed', 'left': '3%', 'top': '42%'},
                    ),
                    html.Div(
                        children=[
                            html.Div(id='asin_cate_one_fig'),
                            html.Div(id='asin_cate_two_fig'),
                            html.Div(id='asin_cate_fsku_fig')
                        ]
                    ),
                    html.Div(
                        id='父ASIN月度汇总',
                        children=[
                            html.Div(id='asin_sum_fig'),
                            html.Div(id='asin_time_fig'),
                            html.Div(id='sub_asin_sum_fig'),
                            html.Div(id='sub_asin_time_fig'),

                        ]),
                    html.Div(
                        id='广告组数据汇总',
                        children=[
                            html.Div(id='ad_comb_fig'),
                            html.Div(id='ad_action_sum_fig'),
                            html.Div(id='ad_group_sum_fig'),
                            html.Div(id='ad_keys_sum_fig'),
                            html.Div(id='ad_key_words_search')
                        ]),
                ]
            ),
        ]),
])

df_pro = pd.read_excel('./static/产品属性表demo.xlsx')


# 上传数据
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # 上传csv文件
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            return df.to_json(), filename
        elif 'xls' in filename:
            # 上传xlsx文件
            df = pd.read_excel(io.BytesIO(decoded))
            print(filename)
            return df.to_json(), filename
    except Exception as e:
        print(e)
        return None, None


# @app.callback([Output('daily_file_store', 'data'),
#                Output('daily_filename_store', 'data'),
#                Output('ad_file_store', 'data'),
#                Output('ad_filename_store', 'data')],
#               [Input('choose_demo', 'on')],
#                [State('daily_file_store', 'data'),
#                 State('daily_filename_store', 'data'),
#                 State('ad_file_store', 'data'),
#                 State('ad_filename_store', 'data')
#                 ])
# def get_demo_data(on, data_daily, daily_file, data_ad, ad_file):
#     if on:
#         df_daily = pd.read_excel('demo_daily.xlsx')
#         df_match = pd.merge(df_daily, df_pro, left_on='sub_asin', right_on='ASIN', how='left')
#         df_match['一级类目'].fillna('其他一级类目', inplace=True)
#         df_match['二级类目'].fillna('其他二级类目', inplace=True)
#         df_daily_json = df_match.to_json()
#
#         df_ad = pd.read_excel('demo_ad.xlsx')
#         df_ad['销量'] = df_ad['7天总销售量(#)']
#         df_ad['销售额'] = df_ad['7天总销售额(￥)']
#         data_info = df_ad[['广告组合名称', '广告活动名称', '广告组名称', '投放', '客户搜索词', '展现量', '点击量', '销量', '销售额', '花费']]
#         df_ad_json = data_info.to_json()
#         return df_daily_json, '演示-日常数据', df_ad_json, '演示-广告数据'
#
#     else:
#         return None, None, None, None

# 上传日常运营数据文件
@app.callback([Output('daily_file_store', 'data'),
               Output('daily_filename_store', 'data')],
              [Input('daily_file', 'contents'),
               Input('choose_demo', 'on')],
              [State('daily_file', 'filename'),
               State('daily_file', 'last_modified'),
               State('daily_file_store', 'data'),
               State('daily_filename_store', 'data')])
def update_output_daily(list_of_contents, on, list_of_names, list_of_dates, file, filename, ):
    if on:
        df = pd.read_excel('./static/demo_daily.xlsx')
        df_match = pd.merge(df, df_pro, left_on='sub_asin', right_on='ASIN', how='left')
        df_match['一级类目'].fillna('其他一级类目', inplace=True)
        df_match['二级类目'].fillna('其他二级类目', inplace=True)
        df_json = df_match.to_json()
        # print(df_json, 'demo')
        return df_json, 'demo'

    elif list_of_contents is not None:
        df_row, filename = parse_contents(list_of_contents, list_of_names, list_of_dates)

        # 解决Excel毫秒时间戳问题
        df = pd.read_json(df_row, convert_dates='date', date_unit='ms')
        # 数据预处理
        df_match = pd.merge(df, df_pro, left_on='sub_asin', right_on='ASIN', how='left')
        df_match['一级类目'].fillna('其他一级类目', inplace=True)
        df_match['二级类目'].fillna('其他二级类目', inplace=True)
        df_json = df_match.to_json()
        # print(df_json, filename)
        return df_json, filename
    else:
        return None, None


# 上传广告数据文件
@app.callback([Output('ad_file_store', 'data'),
               Output('ad_filename_store', 'data')],
              [Input('ad_file', 'contents'),
               Input('choose_demo', 'on')],
              [State('ad_file', 'filename'),
               State('ad_file', 'last_modified'),
               State('ad_file_store', 'data'),
               State('ad_filename_store', 'data')])
def update_output_ad(list_of_contents, on, list_of_names, list_of_dates, file, fname):
    if on:
        df = pd.read_excel('/static/demo_ad.xlsx')
        df['销量'] = df['7天总销售量(#)']
        df['销售额'] = df['7天总销售额(￥)']
        data_info = df[['广告组合名称', '广告活动名称', '广告组名称', '投放', '客户搜索词', '展现量', '点击量', '销量', '销售额', '花费']]
        df_json = data_info.to_json()
        return df_json, 'demo_广告'

    elif list_of_contents is not None:
        # children = [
        #     parse_contents(c, n, d) for c, n, d in
        #     zip(list_of_contents, list_of_names, list_of_dates)]
        df_json, filename = parse_contents(list_of_contents, list_of_names, list_of_dates)

        # 解决毫秒时间戳问题
        df = pd.read_json(df_json, convert_dates='date', date_unit='ms')
        # df = pd.read_json(df_json)
        df['销量'] = df['7天总销售量(#)']
        df['销售额'] = df['7天总销售额(￥)']
        data_info = df[['广告组合名称', '广告活动名称', '广告组名称', '投放', '客户搜索词', '展现量', '点击量', '销量', '销售额', '花费']]
        return data_info.to_json(), filename

    else:
        return None, None


# 数据表格提示
def get_td(mt, file_data, file_name):
    if not (mt and file_data and file_name):
        return 'file_data...', 'file_name...'
    else:
        return file_data[:10], file_name


@app.callback([Output('daily_file_td', 'children'),
               Output('daily_filename_td', 'children')],
              [Input('daily_file_store', 'modified_timestamp')],
              [State('daily_file_store', 'data'),
               State('daily_filename_store', 'data')])
def get_daily_td(mt, daily_file_data, daily_file_name, ):
    return get_td(mt, daily_file_data, daily_file_name)


@app.callback([Output('ad_file_td', 'children'),
               Output('ad_filename_td', 'children')],
              [Input('ad_file_store', 'modified_timestamp')],
              [State('ad_file_store', 'data'),
               State('ad_filename_store', 'data')])
def get_ad_td(mt, ad_file_data, ad_file_name):
    return get_td(mt, ad_file_data, ad_file_name)


# 选择一级类目-下拉菜单
@app.callback(Output('select_cate_one', 'options'),
              [Input('daily_file_store', 'modified_timestamp')],
              [State('daily_file_store', 'data'),
               State('daily_filename_store', 'data')])
def get_cate_one(mt, file_data, filename):
    if not (mt and file_data and filename):
        return [{'label': 'none', 'value': 'none'}]
    else:
        if file_data:
            df = pd.DataFrame(json.loads(file_data))
            cate_list = df['一级类目'].unique()
            result = [{'label': i, 'value': i} for i in cate_list]
            return result


# 选择二级类目-菜单
@app.callback(Output('select_cate_two', 'options'),
              [Input('daily_file_store', 'modified_timestamp'),
               Input('select_cate_one', 'value')],
              [State('daily_file_store', 'data'),
               State('daily_filename_store', 'data')])
def get_cate_two(mt, cate_one, file_data, file_name):
    if not all([mt, cate_one, file_data, file_name]):
        return [{'label': 'none', 'value': 'none'}]
    else:
        if file_data:
            df = pd.DataFrame(json.loads(file_data))
            sub_asin_list = list(df[df['一级类目'] == cate_one]['二级类目'].unique())
            result = [{'label': i, 'value': i} for i in sub_asin_list]
            return result


# 选择-父SKU下拉菜单
@app.callback(Output('select_fsku', 'options'),
              [Input('daily_file_store', 'modified_timestamp'),
               Input('select_cate_one', 'value'),
               Input('select_cate_two', 'value')],
              [State('daily_file_store', 'data'),
               State('daily_filename_store', 'data')])
def get_fsku(mt, cate_one, cate_two, file_data, file_name):
    if not (mt and file_data and file_name):
        return [{'label': 'none', 'value': 'none'}]
    else:
        if file_data:
            df = pd.DataFrame(json.loads(file_data))
            df = df[(df['一级类目'] == cate_one) & (df['二级类目'] == cate_two)]
            if cate_two == '其他二级类目':
                value_list = df['asin'].unique()
                result = [{'label': i, 'value': i} for i in value_list]
                return result
            else:
                value_list = df['父SKU'].unique()
                if any(value_list):
                    result = [{'label': i, 'value': i} for i in value_list]
                    return result
                else:
                    return [{'label': 'none', 'value': 'none'}]


# 选择子sku-下拉菜单
@app.callback(Output('select_sku', 'options'),
              [Input('daily_file_store', 'modified_timestamp'),
               Input('select_cate_one', 'value'),
               Input('select_cate_two', 'value'),
               Input('select_fsku', 'value')],
              [State('daily_file_store', 'data'),
               State('daily_filename_store', 'data')])
def get_sub_asin(mt, cate_one, cate_two, fsku, file_data, file_name):
    if not all([mt, fsku, file_data, file_name]):
        return [{'label': 'none', 'value': 'none'}]
    else:
        if file_data:
            df = pd.DataFrame(json.loads(file_data))
            df = df[(df['一级类目'] == cate_one) & (df['二级类目'] == cate_two)]

            if cate_two == '其他二级类目':
                value_list = df[df['asin'] == fsku]['sub_asin'].unique()

            else:
                value_list = df[df['父SKU'] == fsku]['SKU'].unique()

            if any(value_list):
                result = [{'label': i, 'value': i} for i in value_list]
                return result
            else:
                return [{'label': 'none', 'value': 'none'}]


# 商品信息展示区域
@app.callback(Output('pic_bar', 'children'),
              [Input('daily_file_store', 'modified_timestamp'),
               Input('select_sku', 'value')],
              [State('daily_file_store', 'data')])
def get_pic_bar(mt, sku, data):
    if not all([mt, (sku != 'none'), data, sku]):
        return []
    else:
        res_df = df_pro[df_pro['SKU'] == sku]
        res_df.fillna('未注明', inplace=True)
        asin_dict = res_df.to_dict('list')

        if not any(asin_dict.values()):
            return []
        empty_list = ['未注明']
        goods_name = asin_dict.get('demo名称', empty_list)[0]
        pic_url = asin_dict.get('demo图片链接', empty_list)[0]
        if pic_url:
            pic_url = pic_url.replace('.jpg', '._SL160.jpg')
        asin = asin_dict.get('demoASIN', empty_list)[0]
        color = asin_dict.get('颜色', empty_list)[0]
        size = asin_dict.get('SIZE', empty_list)[0]
        on_shelf_time = asin_dict.get('上架时间', empty_list)[0]
        if on_shelf_time and on_shelf_time != '未注明':
            try:
                on_shelf_time = datetime.datetime.strftime(on_shelf_time, '%Y-%m-%d')
            except:
                pass
        seller = asin_dict.get('店铺', empty_list)[0]

        if seller in ['SK', 'HA']:
            row_url = 'https://www.amazon.co.jp/dp/'
        else:
            row_url = 'https://www.amazon.com/'
        goods_url = row_url + asin
        children = html.Div([
            html.Div(
                className='columns',
                children=[
                    html.Div(html.Img(src=pic_url, width=160, height=160, style={"referrer": "no-referrer"})),
                    html.Div(
                        children=[
                            html.Ul(
                                className='my_ul',
                                children=[
                                    html.Li(html.A('商品链接', href=goods_url, target='blank')),
                                    html.Li('名称：' + str(goods_name)),
                                    html.Li('颜色：' + str(color)),
                                    html.Li('尺寸：' + str(size)),
                                    html.Li('上架时间：' + str(on_shelf_time))
                                ]
                            )
                        ]
                    )
                ])
        ])
        return children


# 一级类目展示
@app.callback(Output('asin_cate_one_fig', 'children'),
              [Input('daily_file_store', 'modified_timestamp')],
              [State('daily_file_store', 'data')])
def get_asin_cate_one_fig(mt, data):
    if not (mt and data):
        return []
    else:
        df = pd.DataFrame(json.loads(data))
        df_sum_asin = df.groupby(by=['一级类目']).agg(
            {'买家访问次数': np.sum, '已订购商品数量': np.sum, '已订购商品销售额': np.sum}).reset_index()
        df_sum_asin['转化率'] = df_sum_asin['已订购商品数量'] / df_sum_asin['买家访问次数']
        df_sum_asin['转化率'] = df_sum_asin['转化率'].apply(lambda x: '{:.2%}'.format(x))
        df_sum_asin.sort_values(by=['买家访问次数'], inplace=True, ascending=False)
        fig = get_daily_sum_fig(df_sum_asin, mode='一级类目', title='各一级类目')
        fig2 = get_daily_table_fig(df_sum_asin, mode='一级类目')
        children = html.Div(
            className='four columns',
            children=[
                dcc.Graph(figure=fig, className='twelve columns'),
                dcc.Graph(figure=fig2, className='twelve columns',
                          style={'height': 100},
                          )
            ]
        )
        return children


# 二级类目展示
@app.callback(Output('asin_cate_two_fig', 'children'),
              [Input('daily_file_store', 'modified_timestamp'),
               Input('select_cate_one', 'value')],
              [State('daily_file_store', 'data')])
def get_asin_cate_two_fig(mt, cate_one, data):
    if not all([mt, cate_one, data]):
        return []
    else:
        df = pd.DataFrame(json.loads(data))
        df = df[df['一级类目'] == cate_one]
        df_sum_asin = df.groupby(by=['二级类目']).agg(
            {'买家访问次数': np.sum, '已订购商品数量': np.sum, '已订购商品销售额': np.sum}).reset_index()
        df_sum_asin['转化率'] = df_sum_asin['已订购商品数量'] / df_sum_asin['买家访问次数']
        df_sum_asin['转化率'] = df_sum_asin['转化率'].apply(lambda x: '{:.2%}'.format(x))
        df_sum_asin.sort_values(by=['买家访问次数'], inplace=True, ascending=False)
        fig = get_daily_sum_fig(df_sum_asin, mode='二级类目', title=cate_one + '-各二级类目-')
        fig2 = get_daily_table_fig(df_sum_asin, mode='二级类目')
        children = html.Div(
            className='four columns',
            children=[
                dcc.Graph(figure=fig, className='twelve columns'),
                dcc.Graph(figure=fig2, className='twelve columns',
                          style={'height': 100},
                          )
            ]
        )

        return children


# 二级类目下的父sku
@app.callback(Output('asin_cate_fsku_fig', 'children'),
              [Input('daily_file_store', 'modified_timestamp'),
               Input('select_cate_one', 'value'),
               Input('select_cate_two', 'value')],
              [State('daily_file_store', 'data')])
def get_asin_cate_two_fig(mt, cate_one, cate_two, data):
    if not all([mt, cate_one, cate_two, (cate_one != 'none'), (cate_two != 'none'), data]):
        return []
    else:
        df = pd.DataFrame(json.loads(data))
        df = df[(df['一级类目'] == cate_one) & (df['二级类目'] == cate_two)]
        if cate_two == '其他二级类目':
            mode = 'asin'
        else:
            mode = '父SKU'
        df_sum_asin = df.groupby(by=[mode]).agg(
            {'买家访问次数': np.sum, '已订购商品数量': np.sum, '已订购商品销售额': np.sum}).reset_index()
        df_sum_asin['转化率'] = df_sum_asin['已订购商品数量'] / df_sum_asin['买家访问次数']
        df_sum_asin['转化率'] = df_sum_asin['转化率'].apply(lambda x: '{:.2%}'.format(x))
        df_sum_asin.sort_values(by=['买家访问次数'], inplace=True, ascending=False)
        fig = get_daily_sum_fig(df_sum_asin, mode=mode, title=cate_two + '-各父sku-')
        fig2 = get_daily_table_fig(df_sum_asin, mode=mode)
        children = html.Div(
            className='four columns',
            children=[
                dcc.Graph(figure=fig, className='twelve columns'),
                dcc.Graph(figure=fig2, className='twelve columns',
                          style={'height': 100},
                          )
            ]
        )

        return children


# 所有父级sku月度汇总
@app.callback(Output('asin_sum_fig', 'children'),
              [Input('daily_file_store', 'modified_timestamp')],
              [State('daily_file_store', 'data')])
def get_asin_sum_fig(mt, data):
    if not (mt and data):
        return []
    else:
        df = pd.read_json(data, convert_dates='date', date_unit='ms')

        df_sum_asin = df.groupby(by=['父SKU']).agg(
            {'买家访问次数': np.sum, '已订购商品数量': np.sum, '已订购商品销售额': np.sum}).reset_index()
        df_sum_asin['转化率'] = df_sum_asin['已订购商品数量'] / df_sum_asin['买家访问次数']
        df_sum_asin['转化率'] = df_sum_asin['转化率'].apply(lambda x: '{:.2%}'.format(x))
        df_sum_asin.sort_values(by=['买家访问次数'], inplace=True, ascending=False)
        fig = get_daily_sum_fig(df_sum_asin, mode='父SKU', title='所有父级sku')
        fig2 = get_daily_table_fig(df_sum_asin, mode='父SKU')
        children = html.Div(
            className='twelve columns',
            children=[
                dcc.Graph(figure=fig, className='twelve columns'),
                dcc.Graph(figure=fig2, className='twelve columns',
                          style={'height': 100},
                          )
            ]
        )

        return children


# 父级SKU月度时域
@app.callback(Output('asin_time_fig', 'children'),
              [Input('daily_file_store', 'modified_timestamp'),
               Input('select_fsku', 'value')],
              [State('daily_file_store', 'data')])
def get_asin_time_fig(mt, fsku, data):
    if not all([mt, fsku, data]):
        return []
    else:
        df = pd.read_json(data, convert_dates='date', date_unit='ms')
        df = df[df['父SKU'] == fsku]
        df_asin = df.groupby(by=['date']).agg(
            {'买家访问次数': np.sum, '已订购商品数量': np.sum}).reset_index()
        df_asin['转化率'] = df_asin['已订购商品数量'] / df_asin['买家访问次数']
        df_asin['转化率'] = df_asin['转化率'].apply(lambda x: '{:.2%}'.format(x))
        fig = get_daily_time_fig(df_asin, title=fsku)
        fig2 = get_daily_table_fig(df_asin, mode='date')
        children = html.Div(
            className='twelve columns',
            children=[
                dcc.Graph(figure=fig, className='twelve columns'),
                dcc.Graph(figure=fig2, className='twelve columns',
                          style={'height': 100},
                          )
            ]
        )

        return children


# 子SKU月度汇总
@app.callback(Output('sub_asin_sum_fig', 'children'),
              [Input('daily_file_store', 'modified_timestamp'),
               Input('select_fsku', 'value')],
              [State('daily_file_store', 'data')])
def get_sub_asin_sum(mt, fsku, data):
    if not (mt and fsku and data):
        return []
    else:
        df = pd.DataFrame(json.loads(data))
        df = df[df['父SKU'] == fsku]
        df_sum_asin = df.groupby(by=['SKU']).agg(
            {'买家访问次数': np.sum, '已订购商品数量': np.sum, '已订购商品销售额': np.sum}).reset_index()
        df_sum_asin['转化率'] = df_sum_asin['已订购商品数量'] / df_sum_asin['买家访问次数']
        df_sum_asin['转化率'] = df_sum_asin['转化率'].apply(lambda x: '{:.2%}'.format(x))
        df_sum_asin.sort_values(by=['买家访问次数'], inplace=True, ascending=False)
        fig = get_daily_sum_fig(df_sum_asin, mode='SKU', title=fsku)
        fig2 = get_daily_table_fig(df_sum_asin, mode='SKU')
        children = html.Div(
            className='twelve columns',
            children=[
                dcc.Graph(figure=fig, className='twelve columns'),
                dcc.Graph(figure=fig2, className='twelve columns',
                          style={'height': 100},
                          )
            ]
        )

        return children


# 子ASIN月度时域图示
@app.callback(Output('sub_asin_time_fig', 'children'),
              [Input('daily_file_store', 'modified_timestamp'),
               Input('select_sku', 'value')],
              [State('daily_file_store', 'data')])
def get_sub_asin_time(mt, sku, data):
    if not (mt and sku and data):
        return []
    else:
        df = pd.read_json(data, convert_dates='date', date_unit='ms')
        # try:
        #     df['date'] = df['date'].apply(lambda x: datetime.datetime.strftime(x, '%m-%d'))
        # except:
        #     pass
        df_one_asin = df[df['SKU'] == sku]
        df_one_asin['转化率'] = df_one_asin['订单商品数量转化率'].apply(lambda x: '{:.2%}'.format(x))
        fig = get_daily_time_fig(df_one_asin, title=sku)
        fig2 = get_daily_table_fig(df_one_asin, mode='date')
        children = html.Div(
            className='twelve columns',
            children=[
                dcc.Graph(figure=fig, className='twelve columns'),
                dcc.Graph(figure=fig2, className='twelve columns',
                          style={'height': 100},
                          )
            ]
        )

        return children


# 选择广告组合名称-菜单
@app.callback(Output('select_ad_comb', 'options'),
              [Input('ad_file_store', 'modified_timestamp')],
              [State('ad_file_store', 'data'),
               State('ad_filename_store', 'data')])
def get_action(mt, file_data, file_name):
    if not (mt and file_data and file_name):
        return [{'label': 'none', 'value': 'none'}]
    else:
        df = pd.DataFrame(json.loads(file_data))
        asin_list = df['广告组合名称'].unique()
        result = [{'label': i, 'value': i} for i in asin_list]
        return result


# 根据广告组合选择广告活动名称-菜单
@app.callback(Output('select_ad_action', 'options'),
              [Input('ad_file_store', 'modified_timestamp'),
               Input('select_ad_comb', 'value')],
              [State('ad_file_store', 'data'),
               State('ad_filename_store', 'data')])
def get_action(mt, ad_comb, file_data, file_name):
    if not all([mt, ad_comb, file_data, file_name]):
        return [{'label': 'none', 'value': 'none'}]
    else:
        df = pd.DataFrame(json.loads(file_data))
        df = df[df['广告组合名称'] == ad_comb]
        asin_list = df['广告活动名称'].unique()
        result = [{'label': i, 'value': i} for i in asin_list]
        return result


# 根据广告组合、广告活动， 选择广告组名称-菜单
@app.callback(Output('select_ad_group', 'options'),
              [Input('ad_file_store', 'modified_timestamp'),
               Input('select_ad_comb', 'value'),
               Input('select_ad_action', 'value')],
              [State('ad_file_store', 'data'),
               State('ad_filename_store', 'data')])
def get_group(mt, ad_comb, ad_action, file_data, file_name):
    if not all([mt, ad_comb, file_data, file_name]):
        return [{'label': 'none', 'value': 'none'}]
    else:
        df = pd.DataFrame(json.loads(file_data))
        df = df[(df['广告组合名称'] == ad_comb) &
                (df['广告活动名称'] == ad_action)]
        sub_asin_list = list(df['广告组名称'].unique())
        result = [{'label': i, 'value': i} for i in sub_asin_list]
        return result


# 选择广告投放名称-菜单
@app.callback(Output('select_ad_words', 'options'),
              [Input('ad_file_store', 'modified_timestamp'),
               Input('select_ad_comb', 'value'),
               Input('select_ad_action', 'value'),
               Input('select_ad_group', 'value')],
              [State('ad_file_store', 'data'),
               State('ad_filename_store', 'data')])
def get_ad_group(mt, ad_comb, ad_action, ad_group, file_data, file_name):
    if not all([mt, ad_comb, ad_action, ad_group, file_data, file_name]):
        return [{'label': 'none', 'value': 'none'}]
    else:
        df = pd.DataFrame(json.loads(file_data))
        df = df[(df['广告组合名称'] == ad_comb) &
                (df['广告活动名称'] == ad_action) &
                (df['广告组名称'] == ad_group)]
        sub_asin_list = list(df['投放'].unique())

        result = [{'label': i, 'value': i} for i in sub_asin_list]
        return result


# 定义绘图辅助函数
def get_ploy_fig(df, title):
    fig = go.Figure()
    df_result = pd.DataFrame()

    df_result.loc[0, '总展现量'] = df['展现量'].sum()
    df_result.loc[0, '总花费'] = df['花费'].sum()
    df_result.loc[0, '总销售额'] = df['销售额'].sum()
    df_result.loc[0, '平均点击率'] = df['点击量'].sum() / df['展现量'].sum()
    df_result.loc[0, '平均acos'] = df['花费'].sum() / df['销售额'].sum()

    for i in ['总花费', '总销售额']:
        try:
            df_result[i] = df_result[i].apply(lambda x: "{:.2f}".format(x))
        except:
            pass
    for i in ['平均点击率', '平均acos']:
        try:
            df_result[i] = df_result[i].apply(lambda x: '{:.2%}'.format(x))
        except:
            pass
    fig.add_trace(go.Table(
        header={'values': list(df_result.columns)},
        cells=dict(
            values=[df_result[k].tolist() for k in df_result.columns[:]],
            align="center")
    ))
    fig.update_layout(dict(
        margin={'l': 0, 't': 0, 'r': 0, 'b': 0},
        height=120,
        title=title + '-广告汇总数据'
    )
    )
    return fig


# 绘制聚合曲线
def get_daily_sum_fig(df_sum_asin, mode, title):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df_sum_asin[mode],
               y=df_sum_asin['买家访问次数'],
               yaxis='y',
               name='访问量',
               text=df_sum_asin['买家访问次数'],
               textposition='auto',
               hovertemplate='%{y}'))
    fig.add_trace(
        go.Scatter(x=df_sum_asin[mode],
                   y=df_sum_asin['已订购商品数量'],
                   yaxis='y2',
                   name='销量',
                   mode='lines+markers', ),
    )
    fig.add_trace(
        go.Scatter(x=df_sum_asin[mode],
                   y=df_sum_asin['转化率'],
                   yaxis='y3',
                   name='转化率',
                   mode='lines+markers',
                   hovertemplate='%{y}%')
    )

    fig.update_layout(
        xaxis=dict(
            domain=[0, 1]
        ),
        yaxis=dict(
            title="访问量",
            titlefont=dict(
                color="#1f77b4"
            ),
            tickfont=dict(
                color="#1f77b4"
            )
        ),
        yaxis2=dict(
            title="销量",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            anchor="free",
            overlaying="y",
            side="left",
            position=0.00725,
        ),
        yaxis3=dict(
            title="转化率",
            titlefont=dict(
                color="#d62728"
            ),
            tickfont=dict(
                color="#d62728"
            ),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        hovermode='x',
        title=title + '聚合曲线'
    )

    return fig


# 绘制日常数据表格
def get_daily_table_fig(df, mode):
    if 'date' in df.columns:
        try:
            df['date'] = df['date'].apply(lambda x: datetime.datetime.strftime(x, '%m-%d'))
        except:
            pass
    fig = go.Figure()
    fig.add_trace(
        go.Table(
            # columnorder=[i+1 for i in range(len(df[mode]))],
            # columnwidth=[30 for each in range(len(df[mode]))],
            header=dict(values=list(df[mode]),
                        fill_color='paleturquoise',
                        align='center'),
            cells=dict(values=df[['买家访问次数', '已订购商品数量', '转化率']].values.tolist(),
                       fill_color='lavender',
                       align='center'),

        )
    )
    fig.update_layout(

        margin=go.layout.Margin(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=4,
        )
    )
    return fig


def get_daily_html_table(df, mode):
    html.Tbody(
        [html.Th(each) for each in (list(df[mode]))],
        html.Tr(
            [html.Td(each) for each in df['卖家访问次数'].values.tolist()]
        ),
        html.Tr(
            html.Td(df['已订购商品数量'].values.tolist())
        ),
        html.Tr(
            html.Td(df['转化率'].values.tolist())
        ),
    )

    pass


# 绘制时域曲线
def get_daily_time_fig(df, title):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df['date'],
            y=df['买家访问次数'],
            name='访问量',
            yaxis='y',
            text=df['买家访问次数'],
            textposition='auto',
            hovertemplate='%{y}',
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['已订购商品数量'],
            name='销量',
            yaxis='y2',
            mode='lines+markers',
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['转化率'],
            name='转化率',
            yaxis='y3',
            mode='lines+markers',
            hovertemplate='%{y}%'
        )
    )

    fig.update_layout(
        xaxis=dict(
            domain=[0, 1]
        ),
        # xaxis_tickformat='%m-%d (.%a)',
        xaxis_tickformat='%m-%d',
        yaxis=dict(
            title="访问量",
            titlefont=dict(
                color="#1f77b4"
            ),
            tickfont=dict(
                color="#1f77b4"
            )
        ),
        yaxis2=dict(
            title="销量",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            anchor="free",
            overlaying="y",
            side="left",
            position=0.00725
        ),
        yaxis3=dict(
            title="转化率",
            titlefont=dict(
                color="#d62728"
            ),
            tickfont=dict(
                color="#d62728"
            ),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        hovermode='x',
        title=title + '时域曲线'
    )

    return fig


# 绘制广告曲线
def get_ad_fig(df, mode, title):
    fig = go.Figure()
    fig_bar = go.Bar(x=df[mode], y=df['展现量'], yaxis='y', name='展现量', text=df['展现量'], textposition='auto',
                     hovertemplate='%{text}')
    fig_line = go.Scatter(x=df[mode], y=df['acos'], yaxis='y2', name='acos', mode='lines+markers',
                          hovertemplate='%{y}%')
    df['acos_目标'] = 30
    fig_line_half = go.Scatter(x=df[mode], y=df['acos_目标'], yaxis='y2', name='30%acos线', mode='lines',
                               hovertemplate='%{y}%')
    fig_line2 = go.Scatter(x=df[mode], y=df['转化率'], yaxis='y3', name='转化率', mode='lines+markers',
                           hovertemplate='%{y}%')
    fig_line3 = go.Scatter(x=df[mode], y=df['花费'], yaxis='y4', name='花费', mode='lines+markers')
    fig_line4 = go.Scatter(x=df[mode], y=df['点击率'], yaxis='y5', name='点击', mode='lines+markers',
                           hovertemplate='%{y}%')
    fig.add_trace(fig_bar)
    fig.add_trace(fig_line)
    fig.add_trace(fig_line2)
    fig.add_trace(fig_line_half)
    fig.add_trace(fig_line3)
    fig.add_trace(fig_line4)
    fig.update_xaxes(tickangle=45)
    fig.update_layout(
        xaxis=dict(
            domain=[0, 1]
        ),
        yaxis=dict(
            title="展现量",
            titlefont=dict(
                color="#1f77b4"
            ),
            tickfont=dict(
                color="#1f77b4"
            )
        ),
        yaxis2=dict(
            title="acos",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            anchor="free",
            overlaying="y",
            side="left",
            position=0.015,
        ),
        yaxis3=dict(
            title="转化率",
            titlefont=dict(
                color="#d62728"
            ),
            tickfont=dict(
                color="#d62728"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=0.95,
        ),
        yaxis4=dict(
            title="花费",
            titlefont=dict(
                color="#993333"
            ),
            tickfont=dict(
                color="#993333"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=0.975,
        ),
        yaxis5=dict(
            title="点击率",
            titlefont=dict(
                color="#339999"
            ),
            tickfont=dict(
                color="#339999"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=0.995,
        ),
        hovermode='x',
        title=title + '广告数据',
    )
    return fig


# 广告数据汇总图示-广告组合图示
@app.callback(Output('ad_comb_fig', 'children'),
              [Input('ad_file_store', 'modified_timestamp')],
              [State('ad_file_store', 'data')])
def get_ad_action_sum_fig(mt, data):
    if not (mt and data):
        return []
    else:
        df = pd.DataFrame(json.loads(data))
        data_group = df.groupby('广告组合名称').agg(
            {'展现量': np.sum, '点击量': np.sum, '销量': np.sum, '销售额': np.sum, '花费': np.sum}).reset_index()
        data_group['acos'] = (data_group['花费'] / data_group['销售额']).apply(lambda x: '{:.2%}'.format(x))
        data_group['点击率'] = (data_group['点击量'] / data_group['展现量']).apply(lambda x: '{:.2%}'.format(x))
        data_group['转化率'] = (data_group['销量'] / data_group['点击量']).apply(lambda x: '{:.2%}'.format(x))
        data_group.sort_values(['展现量'], inplace=True, ascending=False)
        data_group.reset_index(drop=True, inplace=True)
        fig = get_ad_fig(data_group, mode='广告组合名称', title='全部')
        children = html.Div([
            dcc.Graph(figure=fig,
                      className='twelve columns',
                      style={'height': 450})
        ])
        return children


# 广告活动图示
@app.callback(Output('ad_action_sum_fig', 'children'),
              [Input('ad_file_store', 'modified_timestamp'),
               Input('select_ad_comb', 'value')],
              [State('ad_file_store', 'data')])
def get_ad_action_sum_fig(mt, ad_comb, data):
    if not all([mt, ad_comb, data]):
        return []
    else:
        df = pd.DataFrame(json.loads(data))
        df = df[df['广告组合名称'] == ad_comb]
        data_group = df.groupby('广告活动名称').agg(
            {'展现量': np.sum, '点击量': np.sum, '销量': np.sum, '销售额': np.sum, '花费': np.sum}).reset_index()
        data_group['acos'] = (data_group['花费'] / data_group['销售额']).apply(lambda x: '{:.2%}'.format(x))
        data_group['点击率'] = (data_group['点击量'] / data_group['展现量']).apply(lambda x: '{:.2%}'.format(x))
        data_group['转化率'] = (data_group['销量'] / data_group['点击量']).apply(lambda x: '{:.2%}'.format(x))
        data_group.sort_values(['展现量'], inplace=True, ascending=False)
        data_group.reset_index(drop=True, inplace=True)
        fig = get_ad_fig(data_group, mode='广告活动名称', title=ad_comb)
        children = html.Div([
            dcc.Graph(figure=fig,
                      className='six columns',
                      style={'height': 450})
        ])
        return children


# 广告组具体图示
@app.callback(Output('ad_group_sum_fig', 'children'),
              [Input('ad_file_store', 'modified_timestamp'),
               Input('select_ad_comb', 'value'),
               Input('select_ad_action', 'value')],
              [State('ad_file_store', 'data'),
               State('ad_filename_store', 'data')])
def get_ad_group_fig(mt, ad_comb, ad_action, data, filename):
    if not all([mt, ad_comb, ad_action, data]):
        return []
    else:
        df_row = pd.DataFrame(json.loads(data))
        data_action = df_row[(df_row['广告组合名称'] == ad_comb) &
                             (df_row['广告活动名称'] == ad_action)]
        data_group = data_action.groupby('广告组名称').agg(
            {'展现量': np.sum, '点击量': np.sum, '销量': np.sum, '销售额': np.sum, '花费': np.sum}).reset_index()

        data_group['acos'] = (data_group['花费'] / data_group['销售额']).apply(lambda x: '{:.2%}'.format(x))
        data_group['点击率'] = (data_group['点击量'] / data_group['展现量']).apply(lambda x: '{:.2%}'.format(x))
        data_group['转化率'] = (data_group['销量'] / data_group['点击量']).apply(lambda x: '{:.2%}'.format(x))
        data_group.sort_values(['展现量'], inplace=True, ascending=False)
        data_group.reset_index(drop=True, inplace=True)
        fig = get_ad_fig(data_group, mode='广告组名称', title=ad_comb + '/' + ad_action)
        children = html.Div([
            dcc.Graph(figure=fig,
                      className='six columns'),
        ])
        return children


# 广告投放具体图示
@app.callback(Output('ad_keys_sum_fig', 'children'),
              [Input('ad_file_store', 'modified_timestamp'),
               Input('select_ad_comb', 'value'),
               Input('select_ad_action', 'value'),
               Input('select_ad_group', 'value')],
              [State('ad_file_store', 'data'),
               State('ad_filename_store', 'data')])
def get_ad_group_fig(mt, ad_comb, ad_action, ad_group, data, filename):
    if not all([mt, ad_comb, ad_action, ad_group, data]):
        return []
    else:
        df_row = pd.DataFrame(json.loads(data))
        data_action = df_row[(df_row['广告组合名称'] == ad_comb) &
                             (df_row['广告活动名称'] == ad_action) &
                             (df_row['广告组名称'] == ad_group)]
        data_group = data_action.groupby('投放').agg(
            {'展现量': np.sum, '点击量': np.sum, '销量': np.sum, '销售额': np.sum, '花费': np.sum}).reset_index()
        data_group['acos'] = (data_group['花费'] / data_group['销售额']).apply(lambda x: '{:.2%}'.format(x))
        data_group['点击率'] = (data_group['点击量'] / data_group['展现量']).apply(lambda x: '{:.2%}'.format(x))
        data_group['转化率'] = (data_group['销量'] / data_group['点击量']).apply(lambda x: '{:.2%}'.format(x))
        data_group.sort_values(['展现量'], inplace=True, ascending=False)
        data_group.reset_index(drop=True, inplace=True)
        fig = get_ad_fig(data_group, mode='投放', title=ad_comb + "/" + ad_action + "/" + ad_group)
        children = html.Div([
            dcc.Graph(figure=fig, className='twelve columns'),
        ])
        return children


# 广告搜索词具体图示
@app.callback(Output('ad_key_words_search', 'children'),
              [Input('ad_file_store', 'modified_timestamp'),
               Input('select_ad_comb', 'value'),
               Input('select_ad_action', 'value'),
               Input('select_ad_group', 'value'),
               Input('select_ad_words', 'value')],
              [State('ad_file_store', 'data'),
               State('ad_filename_store', 'data')])
def get_ad_words_fig(mt, ad_comb, ad_action, ad_group, ad_words, data, filename):
    if not all([mt, ad_comb, ad_action, ad_group, ad_words, data]):
        return []
    else:
        df_row = pd.DataFrame(json.loads(data))
        data_action = df_row[(df_row['广告组合名称'] == ad_comb) &
                             (df_row['广告活动名称'] == ad_action) &
                             (df_row['广告组名称'] == ad_group) &
                             (df_row['投放'] == ad_words)]
        data_group = data_action.groupby('客户搜索词').agg(
            {'展现量': np.sum, '点击量': np.sum, '销量': np.sum, '销售额': np.sum, '花费': np.sum}).reset_index()

        data_group['acos'] = (data_group['花费'] / data_group['销售额']).apply(lambda x: '{:.2%}'.format(x))
        data_group['点击率'] = (data_group['点击量'] / data_group['展现量']).apply(lambda x: '{:.2%}'.format(x))
        data_group['转化率'] = (data_group['销量'] / data_group['点击量']).apply(lambda x: '{:.2%}'.format(x))
        data_group.sort_values(['展现量'], inplace=True, ascending=False)
        data_group.reset_index(drop=True, inplace=True)
        fig = get_ad_fig(data_group, mode='客户搜索词', title=ad_words)
        children = html.Div([
            dcc.Graph(figure=fig, className='twelve columns'),
        ])
        return children


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/2019':
        return page_2019
    else:
        return index_page


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
if __name__ == '__main__':
    app.run_server(debug=True, port=8800)
