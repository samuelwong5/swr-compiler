import csv
import os
import requests
import sys

from plotly.graph_objs import *
import plotly.plotly as py
    
def create_monthly_bar(file_paths):
    ssfiles = map(lambda x: x + 'serverSummary.csv', file_paths)
    create(ssfiles)
    
    bot_data = [['Mar15','Apr15','May15'],[]]   
    ccfiles = map(lambda x: x + 'C&CServers.csv', file_paths)
    for ccf in ccfiles:
        with open(ccf) as csv_file:
            dreader = csv.DictReader(csv_file)
            hold = []
            for row in dreader:
                if row['ip'] not in hold:
                   hold.append(row['ip'])        
            bot_data[1].append(len(hold))
    generate_chart(bot_data, ['Month', 'Botnet (C&Cs)'], 'BotCCDis', 'Botnet (C&Cs) security event distribution')
    
    cc_data = [['IRC','HTTP','P2P'],[0,0,0]]
    with open(ccfiles[2]) as csv_file:
        dreader = csv.DictReader(csv_file)
        hold = []
        for row in dreader:
            if row['ip'] not in hold:
                if row['channel'] == '-': #HTTP
                    cc_data[1][1] += 1 
                else:                     #IRC
                    cc_data[1][0] += 1  
                hold.append(row['ip'])                 
    generate_chart(cc_data, ['Communication Type', 'Count'], 'BotCCType', 'Botnet (C&Cs) by communication type')
   
    bot_data = [['Mar15','Apr15','May15'],[]]   
    bnfiles = map(lambda x: x + 'botnetDailyMax.csv', file_paths)
    for bnf in bnfiles:
        with open(bnf) as csv_file:
            dreader = csv.DictReader(csv_file)
            total_count = 0
            for row in dreader:
                if row['Count'] != '':
                    total_count += int(row['Count'])
            bot_data[1].append(total_count)
    generate_chart(bot_data, ['Month', 'Botnet (Bots)'], 'BotBotsDis', 'Botnet (Bots) security event distribution')
      
    
def create(file_paths):
    data = []
    headers = []
    for j in range(len(file_paths)):
        data.append([])
        with open(file_paths[j]) as csv_file:
            dreader = csv.DictReader(csv_file)
            headers = dreader.fieldnames
            for row in dreader:
                for i in range(len(headers)):
                    if (len(data[j]) < len(headers)):
                        data[j].append([])
                    data[j][i].append(row[headers[i]])

    server_dis_headers = ['Month','Defacement','Phishing','Malware']                
    server_dis = [['Mar15','Apr15','May15'],[],[],[]]
    for i in range(3):
        for j in range(3):
            server_dis[i+1].append(data[j][i+1][1])
    generate_chart(server_dis, server_dis_headers, 'ServerRelated', 'Server Related security events distribution','stack')

    gen = [(1,'Defacement'),(2,'Phishing'),(3,'Malware')]
    gen_headers = ['Month','URL','Domain','IP']                
    gen_data = [['Mar15','Apr15','May15'],[],[],[]]
    for g in gen:
        index, type = g
        for i in range(3):
            gen_data[i+1] = []
            for j in range(3):
                gen_data[i+1].append(data[j][index][i+1])    
        generate_chart(gen_data, gen_headers, type + 'Gen', type + ' General Statistics')
    
    url_ip_headers = ['Month', 'URL/IP Ratio']
    url_data = [['Mar15','Apr15','May15'],[]]
    for g in gen:
        index, type = g
        url_data[1] = []
        for j in range(3):
            url_data[1].append(round(float(data[j][index][1]) / float(data[j][index][3]),2))  
        generate_chart(url_data, url_ip_headers, type + 'URLIP', type + ' URL/IP Ratio')
 
    

def generate_chart(data, headers, png_name, name, bar_mode='group'):
    bars = []
    for i in range(1,len(data)):
        if (max == -1):
            bars.append(Bar(
                            x=data[0],
                            y=data[i],
                            name=headers[i]
                        ))
        else:
            bars.append(Bar(
                            x=(data[0])[:10],
                            y=(data[i])[:10],
                            name=headers[i]
                        ))
                        
    # misc. chart setup
    chart_data = Data(bars)
    chart_title = name
    if (len(data)==2 or bar_mode=='stack'):
        total_len = 10 if len(data[0]) > 10 else len(data[0])
        total = map(lambda x: int(x) if (type(x) is str) else x, data[1][:total_len])
        if bar_mode=='stack':
            for i in range(2, len(data)):
                total = map(sum, zip(total, map(int,data[i][:total_len])))
        max_len = reduce(lambda x,y: x if x>y else y, total)
        if len(data) > 2:
            all_columns =  map(lambda x: int(x), sum([(data[x][:10]) for x in range(1,len(data))],[]))
            all_columns_height = list(all_columns)
            for i in range(len(all_columns_height) - 1, total_len, -1):
                j = total_len
                all_columns_height[i] *= 0.4
                while (i - j >= 0):
                    all_columns_height[i] += all_columns_height[i-j]
                    j += total_len
            for i in range(0, 10 if 10 <= total_len else total_len):
                all_columns_height[i] /= 2
            all_columns += total[:10]
            all_columns_height += total[:10]
        else:
            all_columns = total[:10]
            all_columns_height = total[:10] 
        annt = [Annotation(
                x=xi,
                y=zi,
                text=str(int(yi)),
                xanchor='center',
                yanchor='bottom',
                showarrow=False,
                ) for xi, yi, zi in filter(lambda x: x[1] > (max_len / 8), 
                                   zip(data[0][:10] * (len(data)),
                                       all_columns, 
                                       all_columns_height
                                   ))]

    else:
        len_x = range(len(data[0]))
        annotation_x = map(lambda x: x-0.27, len_x) + len_x + map(lambda x: x+0.27, len_x)
        annotation_y = data[1] + data[2] + data[3]
        annt=[Annotation(
                    x=xi,
                    y=yi,
                    text=str(yi),
                    xanchor='center',
                    yanchor='bottom',
                    showarrow=False,
                ) for xi, yi in zip(annotation_x, annotation_y)]
        
    layout = Layout(
        title=chart_title,
        font=Font(
            size=16
            ),
        barmode=bar_mode,
        annotations=annt
        )    
    fig = Figure(data=chart_data,layout=layout)
    
    # plot and download chart
    plot_url = py.plot(fig, chart_title)
    print_no_newline('  ' + png_name + '.png')
    download_png(plot_url, 'latex/' + png_name + '.png')    
    
# util function for printing to terminal without newline char 
def print_no_newline(text):
    sys.stdout.write('  ' + text + (' ' * (71 - len(text))))
    sys.stdout.flush()  
    
def download_png(url, output):
    r = requests.get(url + '.png', stream=True)
    if r.status_code == 200:
        dir = os.path.dirname(output)
        if not os.path.exists(dir): # Check that parent dir exists
            os.makedirs(dir)
        with open(output, 'w+b') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    print('[DONE]') 
   
if __name__ == "__main__":    
    create_monthly_bar()
 