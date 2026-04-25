import React, { useState, useEffect } from 'react';
import { Layout, Menu, Card, Row, Col, Statistic, Table, Typography, Tabs, Alert, Spin, Switch, Button } from 'antd';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { 
  SecurityScanOutlined, 
  UserOutlined, 
  KeyOutlined, 
  CodeOutlined, 
  DashboardOutlined, 
  FileTextOutlined,
  GlobalOutlined,
  ThunderboltOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SearchOutlined,
  MailOutlined
} from '@ant-design/icons';
import axios from 'axios';
import 'antd/dist/reset.css';
import './index.css';
import Background from './Background';
import NetworkMesh from './NetworkMesh';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

const COLORS = ['#00ff41', '#00c49f', '#ffbb28', '#ff8042', '#8884d8'];

function App() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activePage, setActivePage] = useState('dashboard');
  const [rescanLoading, setRescanLoading] = useState(false);
  const [theme, setTheme] = useState(localStorage.getItem('hades-theme') || 'dark');

  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('hades-theme', theme);
  }, [theme]);

  const toggleTheme = (checked) => {
    setTheme(checked ? 'dark' : 'light');
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/dashboard');
      setDashboardData(response.data);
      setLoading(false);
      setError(null);
    } catch (err) {
      setError('Failed to fetch system telemetry');
      setLoading(false);
    }
  };

  const handleRescan = () => {
    setRescanLoading(true);
    setTimeout(() => {
      fetchDashboardData();
      setRescanLoading(false);
    }, 1500);
  };

  const isDark = theme === 'dark';
  const themeAccent = isDark ? '#00ff41' : '#ff4136';

  const authColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text) => <Text style={{ color: 'var(--text-muted)' }}>{new Date(text).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</Text>,
    },
    {
      title: 'Service',
      dataIndex: 'service',
      key: 'service',
      render: (service) => (
        <span 
          className="status-tag status-tag-active" 
          style={{ 
            background: service?.toLowerCase() === 'ftp' ? 'rgba(255, 169, 64, 0.1)' : 'rgba(24, 144, 255, 0.1)', 
            color: service?.toLowerCase() === 'ftp' ? '#ffa940' : (isDark ? '#1890ff' : '#096dd9'), 
            border: service?.toLowerCase() === 'ftp' ? '1px solid rgba(255, 169, 64, 0.2)' : '1px solid rgba(24, 144, 255, 0.2)' 
          }}
        >
          {service?.toUpperCase() || 'SSH'}
        </span>
      ),
    },
    {
      title: 'Source IP',
      dataIndex: 'src_ip',
      key: 'src_ip',
      render: (text) => <Text style={{ color: 'var(--text-main)' }}>{text}</Text>
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
      render: (text) => <Text style={{ color: 'var(--text-main)' }}>{text}</Text>
    },
    {
      title: 'Password',
      dataIndex: 'password',
      key: 'password',
      render: (text) => <Text code style={{ background: 'var(--glass-bg)', color: 'var(--text-muted)', border: 'none' }}>{text.substring(0, 20)}</Text>,
    },
    {
      title: 'Status',
      dataIndex: 'success',
      key: 'success',
      render: (success) => (
        <span className={`status-tag ${success ? 'status-tag-active' : 'status-tag-failed'}`}>
          {success ? <><CheckCircleOutlined /> ALLOWED</> : <><CloseCircleOutlined /> DENIED</>}
        </span>
      ),
    },
  ];

  const commandColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text) => <Text style={{ color: 'var(--text-muted)' }}>{new Date(text).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</Text>,
    },
    {
      title: 'Session ID',
      dataIndex: 'session_id',
      key: 'session_id',
    },
    {
      title: 'Command',
      dataIndex: 'command',
      key: 'command',
      render: (text) => <Text code style={{ background: isDark ? 'rgba(0,255,65,0.05)' : 'rgba(255,65,54,0.05)', color: 'var(--neon-accent)', border: 'none' }}>{text}</Text>,
    },
    {
      title: 'Arguments',
      dataIndex: 'args',
      key: 'args',
      render: (text) => <Text style={{ color: 'var(--text-muted)' }}>{text || '-'}</Text>,
    },
  ];

  const dnsColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text) => <Text style={{ color: 'var(--text-muted)' }}>{new Date(text).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</Text>,
    },
    {
      title: 'Source IP',
      dataIndex: 'src_ip',
      key: 'src_ip',
      render: (text) => <Text style={{ color: 'var(--text-main)' }}>{text}</Text>
    },
    {
      title: 'Query Name',
      dataIndex: 'query_name',
      key: 'query_name',
      render: (text) => <Text code style={{ background: 'var(--glass-bg)', color: 'var(--neon-accent)', border: 'none' }}>{text}</Text>,
    },
    {
      title: 'Type',
      dataIndex: 'query_type',
      key: 'query_type',
      render: (text) => (
        <span className="status-tag status-tag-active" style={{ background: 'rgba(114, 46, 209, 0.1)', color: '#722ed1', border: '1px solid rgba(114, 46, 209, 0.2)' }}>
          {text}
        </span>
      ),
    },
  ];

  const httpColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text) => <Text style={{ color: 'var(--text-muted)' }}>{new Date(text).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</Text>,
    },
    {
      title: 'Source IP',
      dataIndex: 'src_ip',
      key: 'src_ip',
      render: (text) => <Text style={{ color: 'var(--text-main)' }}>{text}</Text>
    },
    {
      title: 'Method',
      dataIndex: 'method',
      key: 'method',
      render: (text) => (
        <span className="status-tag status-tag-active" style={{ background: 'rgba(255, 65, 54, 0.1)', color: '#ff4136', border: '1px solid rgba(255, 65, 54, 0.2)' }}>
          {text}
        </span>
      ),
    },
    {
      title: 'Path',
      dataIndex: 'path',
      key: 'path',
      render: (text) => <Text code style={{ background: 'var(--glass-bg)', color: 'var(--neon-accent)', border: 'none' }}>{text}</Text>,
    },
    {
      title: 'User Agent',
      dataIndex: 'user_agent',
      key: 'user_agent',
      render: (text) => <Text style={{ color: 'var(--text-muted)', fontSize: 11 }}>{text?.substring(0, 40)}...</Text>,
    },
  ];

  const smtpColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text) => <Text style={{ color: 'var(--text-muted)' }}>{new Date(text).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</Text>,
    },
    {
      title: 'Source IP',
      dataIndex: 'src_ip',
      key: 'src_ip',
      render: (text) => <Text style={{ color: 'var(--text-main)' }}>{text}</Text>
    },
    {
      title: 'From',
      dataIndex: 'mail_from',
      key: 'mail_from',
      render: (text) => <Text style={{ color: 'var(--neon-accent)' }}>{text || '-'}</Text>
    },
    {
      title: 'To',
      dataIndex: 'rcpt_to',
      key: 'rcpt_to',
      render: (text) => <Text style={{ color: 'var(--text-muted)', fontSize: 11 }}>{text?.substring(0, 30)}</Text>
    },
    {
      title: 'Subject',
      dataIndex: 'subject',
      key: 'subject',
      render: (text) => <Text style={{ color: 'var(--text-main)', fontWeight: 500 }}>{text || '(No Subject)'}</Text>
    },
    {
      title: 'Credentials',
      key: 'creds',
      render: (_, record) => (
        record.username ? (
          <Text code style={{ fontSize: 10, background: 'rgba(255,169,64,0.1)', color: '#ffa940', border: 'none' }}>
            {record.username}:{record.password}
          </Text>
        ) : <Text type="secondary">-</Text>
      )
    }
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: 'var(--bg-page)' }}>
        <Background theme={theme} />
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '50px', background: 'var(--bg-page)', minHeight: '100vh' }}>
        <Background theme={theme} />
        <Alert message="System Error" description={error} type="error" showIcon />
      </div>
    );
  }

  const { 
    summary, 
    top_source_ips, 
    top_usernames, 
    top_passwords, 
    top_commands, 
    top_dns_queries,
    daily_attempts, 
    recent_auth, 
    recent_commands, 
    recent_sessions,
    recent_dns,
    recent_http,
    recent_smtp,
    top_http_paths,
    top_smtp_senders,
    top_smtp_recipients,
    top_attacked_ports
  } = dashboardData;

  const renderDashboard = () => {
    const renderIntegratedChart = (title, data, dataKey, nameKey) => (
      <Col span={8}>
        <div className="glass-panel" style={{ padding: '20px 24px' }}>
          <Title level={5} style={{ color: 'var(--text-main)', marginBottom: 20, textTransform: 'uppercase', letterSpacing: 1.5, fontSize: 14 }}>{title}</Title>
          <div style={{ display: 'flex', alignItems: 'center', height: 180 }}>
            <div style={{ flex: 1.4, height: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.slice(0, 5)}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={8}
                    dataKey={dataKey}
                    stroke="none"
                  >
                    {data.slice(0, 5).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      background: isDark ? 'rgba(20, 20, 25, 0.95)' : 'rgba(255, 255, 255, 0.95)', 
                      border: '1px solid var(--glass-border)', 
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                    }}
                    itemStyle={{ color: 'var(--text-main)', fontSize: 12 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div style={{ flex: 1, paddingLeft: 16, display: 'flex', flexDirection: 'column', justifyContent: 'center', borderLeft: '1px solid var(--glass-border)' }}>
              {data.slice(0, 5).map((entry, index) => (
                <div key={index} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', overflow: 'hidden' }}>
                    <div style={{ width: 8, height: 8, borderRadius: '2px', background: COLORS[index % COLORS.length], marginRight: 10, flexShrink: 0 }} />
                    <Text ellipsis title={entry[nameKey]} style={{ color: 'var(--text-muted)', fontSize: 11, maxWidth: 65, fontWeight: 500 }}>
                      {entry[nameKey]}
                    </Text>
                  </div>
                  <Text style={{ color: 'var(--neon-accent)', fontWeight: 700, fontSize: 13, fontFamily: 'Source Code Pro' }}>
                    {entry[dataKey]}
                  </Text>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Col>
    );

    const renderPortAttackChart = (title, data) => (
      <Col span={8}>
        <div className="glass-panel" style={{ padding: '20px 24px' }}>
          <Title level={5} style={{ color: 'var(--text-main)', marginBottom: 20, textTransform: 'uppercase', letterSpacing: 1.5, fontSize: 14 }}>{title}</Title>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={data} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" vertical={false} />
              <XAxis dataKey="port" stroke="var(--text-muted)" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--text-muted)" fontSize={10} tickLine={false} axisLine={false} />
              <Tooltip 
                cursor={{ fill: 'var(--glass-bg)' }}
                contentStyle={{ 
                  background: isDark ? 'rgba(20, 20, 25, 0.95)' : 'rgba(255, 255, 255, 0.95)', 
                  border: '1px solid var(--glass-border)', 
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="count" fill="var(--neon-accent)" radius={[4, 4, 0, 0]} barSize={25}>
                {data?.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Col>
    );

    return (
      <>
        <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
          <Col xs={24} sm={12} lg={4} xl={4} style={{ flex: '1 0 20%', maxWidth: '20%' }}>
            <div className="glass-panel" style={{ padding: 24 }}>
              <Statistic
                title="Total Incursions"
                value={summary.total_auth_attempts}
                prefix={<SecurityScanOutlined />}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={4} xl={4} style={{ flex: '1 0 20%', maxWidth: '20%' }}>
            <div className="glass-panel" style={{ padding: 24 }}>
              <Statistic
                title="Breaches Detected"
                value={summary.successful_logins}
                prefix={<UserOutlined />}
                valueStyle={{ color: 'var(--neon-accent)' }}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={4} xl={4} style={{ flex: '1 0 20%', maxWidth: '20%' }}>
            <div className="glass-panel" style={{ padding: 24 }}>
              <Statistic
                title="Deflected Attacks"
                value={summary.failed_logins}
                prefix={<KeyOutlined />}
                valueStyle={{ color: '#ff4136' }}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={4} xl={4} style={{ flex: '1 0 20%', maxWidth: '20%' }}>
            <div className="glass-panel" style={{ padding: 24 }}>
              <Statistic
                title="DNS Queries Intercepted"
                value={summary.total_dns_queries || 0}
                prefix={<SearchOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={4} xl={4} style={{ flex: '1 0 16.66%', maxWidth: '16.66%' }}>
            <div className="glass-panel" style={{ padding: 24 }}>
              <Statistic
                title="HTTP Requests Deflected"
                value={summary.total_http_requests || 0}
                prefix={<GlobalOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
            </div>
          </Col>
          <Col xs={24} sm={12} lg={4} xl={4} style={{ flex: '1 0 16.66%', maxWidth: '16.66%' }}>
            <div className="glass-panel" style={{ padding: 24 }}>
              <Statistic
                title="Emails Intercepted"
                value={summary.total_smtp_interactions || 0}
                prefix={<MailOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </div>
          </Col>
        </Row>

        <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
          <Col span={16}>
            <div className="glass-panel" style={{ padding: 24 }}>
              <Title level={5} style={{ color: 'var(--text-main)', marginBottom: 24, textTransform: 'uppercase', letterSpacing: 1.5 }}>Traffic Velocity</Title>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={daily_attempts.slice(0, 10).reverse()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" vertical={false} />
                  <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip 
                    contentStyle={{ background: isDark ? 'rgba(13, 13, 15, 0.9)' : 'rgba(255, 255, 255, 0.9)', border: '1px solid var(--glass-border)', borderRadius: '8px' }}
                    itemStyle={{ color: 'var(--neon-accent)' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="count" 
                    stroke="var(--neon-accent)" 
                    strokeWidth={3} 
                    dot={{ r: 4, fill: 'var(--neon-accent)', strokeWidth: 2, stroke: 'var(--bg-page)' }}
                    activeDot={{ r: 6, strokeWidth: 0 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Col>
          <Col span={8}>
            <div className="glass-panel" style={{ padding: 24 }}>
              <Title level={5} style={{ color: 'var(--text-main)', marginBottom: 24, textTransform: 'uppercase', letterSpacing: 1.5 }}>Threat Origin</Title>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={top_source_ips.slice(0, 5)} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" horizontal={false} />
                  <XAxis type="number" hide />
                  <YAxis dataKey="src_ip" type="category" stroke="var(--text-muted)" fontSize={10} width={100} tickLine={false} axisLine={false} />
                  <Tooltip 
                    cursor={{ fill: 'var(--glass-bg)' }}
                    contentStyle={{ background: isDark ? 'rgba(13, 13, 15, 0.9)' : 'rgba(255, 255, 255, 0.9)', border: '1px solid var(--glass-border)', borderRadius: '8px' }}
                  />
                  <Bar dataKey="count" fill="var(--neon-accent)" radius={[0, 4, 4, 0]} barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Col>
        </Row>

        <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
          {renderIntegratedChart('Top Usernames', top_usernames, 'count', 'username')}
          {renderIntegratedChart('Top Passwords', top_passwords, 'count', 'password')}
          {renderIntegratedChart('Top Commands', top_commands, 'count', 'command')}
        </Row>

        <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
          {renderIntegratedChart('Top DNS Queries', top_dns_queries, 'count', 'query_name')}
          {renderIntegratedChart('Top HTTP Paths', top_http_paths, 'count', 'path')}
          {renderIntegratedChart('Top SMTP Senders', top_smtp_senders, 'count', 'mail_from')}
        </Row>
        <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
          {renderIntegratedChart('Top SMTP Recipients', top_smtp_recipients, 'count', 'rcpt_to')}
          {renderPortAttackChart('Port Attack Intensity', top_attacked_ports)}
          <Col span={8}>
            <div className="glass-panel" style={{ height: 264, padding: 0, overflow: 'hidden', position: 'relative' }}>
              <NetworkMesh data={dashboardData} theme={theme} compact={true} showGraph={true} showList={false} />
            </div>
          </Col>
        </Row>
      </>
    );
  };

  const renderIntelLogs = () => (
    <div className="glass-panel" style={{ padding: 24 }}>
      <Tabs defaultActiveKey="1" className="custom-tabs">
        <TabPane tab={<span style={{ color: 'var(--text-main)' }}><SecurityScanOutlined /> Authentication Intel</span>} key="1">
          <Table
            columns={authColumns}
            dataSource={recent_auth}
            rowKey="id"
            pagination={{ pageSize: 8 }}
            scroll={{ x: true }}
          />
        </TabPane>
        <TabPane tab={<span style={{ color: 'var(--text-main)' }}><CodeOutlined /> Executed Commands</span>} key="2">
          <Table
            columns={commandColumns}
            dataSource={recent_commands}
            rowKey="id"
            pagination={{ pageSize: 8 }}
            scroll={{ x: true }}
          />
        </TabPane>
        <TabPane tab={<span style={{ color: 'var(--text-main)' }}><GlobalOutlined /> DNS Query Intel</span>} key="3">
          <Table
            columns={dnsColumns}
            dataSource={recent_dns}
            rowKey="id"
            pagination={{ pageSize: 8 }}
            scroll={{ x: true }}
          />
        </TabPane>
        <TabPane tab={<span style={{ color: 'var(--text-main)' }}><GlobalOutlined /> HTTP Attack Intel</span>} key="4">
          <Table
            columns={httpColumns}
            dataSource={recent_http}
            rowKey="id"
            pagination={{ pageSize: 8 }}
            scroll={{ x: true }}
          />
        </TabPane>
        <TabPane tab={<span style={{ color: 'var(--text-main)' }}><MailOutlined /> SMTP Attack Intel</span>} key="5">
          <Table
            columns={smtpColumns}
            dataSource={recent_smtp}
            rowKey="id"
            pagination={{ pageSize: 8 }}
            scroll={{ x: true }}
          />
        </TabPane>
      </Tabs>
    </div>
  );

  const renderNetworkMesh = () => (
    <div style={{ padding: '0 20px' }}>
      <NetworkMesh data={dashboardData} theme={theme} showGraph={false} showList={true} />
    </div>
  );

  return (
    <Layout style={{ minHeight: '100vh', background: 'transparent' }}>
      <Background theme={theme} />
      <Sider width={260} breakpoint="lg" collapsedWidth="0" style={{ background: 'var(--bg-sidebar) !important', backdropFilter: 'blur(10px)' }}>
        <div className="logo">
          <SecurityScanOutlined /> <span>HADES</span>
        </div>
        <Menu 
          theme={isDark ? "dark" : "light"} 
          mode="inline" 
          selectedKeys={[activePage]}
          onClick={({ key }) => setActivePage(key)}
          style={{ background: 'transparent' }}
        >
          <Menu.Item key="dashboard" icon={<DashboardOutlined />}>
            Operations Center
          </Menu.Item>
          <Menu.Item key="intel" icon={<FileTextOutlined />}>
            Intel Logs
          </Menu.Item>
          <Menu.Item key="mesh" icon={<GlobalOutlined />}>
            Network Mesh
          </Menu.Item>
        </Menu>
      </Sider>
      
      <Layout style={{ background: 'transparent' }}>
        <Header style={{ height: 72, display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--bg-header) !important' }}>
          <div className="header-title">
            <ThunderboltOutlined /> COMMAND & CONTROL
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Text style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 700, letterSpacing: 1 }}>MODE</Text>
              <Switch checked={isDark} onChange={toggleTheme} size="small" style={{ background: 'var(--glass-border)' }} />
            </div>
            <Button 
              type="primary" 
              ghost 
              icon={<ReloadOutlined spin={rescanLoading} />} 
              onClick={handleRescan}
              style={{ borderColor: 'var(--glass-border)', color: 'var(--neon-accent)', borderRadius: 8 }}
            >
              RESCAN
            </Button>
          </div>
        </Header>
        
        <Content style={{ padding: '32px 24px', overflowY: 'auto' }}>
          {activePage === 'dashboard' ? renderDashboard() : 
           activePage === 'intel' ? renderIntelLogs() : 
           renderNetworkMesh()}
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
