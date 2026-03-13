import React, { useState, useEffect } from 'react';
import { Layout, Menu, Card, Row, Col, Statistic, Table, Typography, Tabs, Alert, Spin } from 'antd';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { SecurityScanOutlined, UserOutlined, KeyOutlined, CodeOutlined, DashboardOutlined, FileTextOutlined } from '@ant-design/icons';
import axios from 'axios';
import 'antd/dist/reset.css';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

function App() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
      setError('Failed to fetch dashboard data');
      setLoading(false);
    }
  };

  const authColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text) => new Date(text).toLocaleString(),
    },
    {
      title: 'Source IP',
      dataIndex: 'src_ip',
      key: 'src_ip',
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: 'Password',
      dataIndex: 'password',
      key: 'password',
      render: (text) => <Text code>{text.substring(0, 20)}...</Text>,
    },
    {
      title: 'Success',
      dataIndex: 'success',
      key: 'success',
      render: (success) => (
        <span style={{ color: success ? 'green' : 'red' }}>
          {success ? 'Success' : 'Failed'}
        </span>
      ),
    },
  ];

  const commandColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text) => new Date(text).toLocaleString(),
    },
    {
      title: 'Session ID',
      dataIndex: 'session_id',
      key: 'session_id',
      render: (text) => <Text code>{text.substring(0, 8)}...</Text>,
    },
    {
      title: 'Command',
      dataIndex: 'command',
      key: 'command',
      render: (text) => <Text code>{text}</Text>,
    },
    {
      title: 'Args',
      dataIndex: 'args',
      key: 'args',
    },
    {
      title: 'Duration',
      dataIndex: 'duration',
      key: 'duration',
      render: (duration) => `${duration?.toFixed(2)}s`,
    },
  ];

  const sessionColumns = [
    {
      title: 'Session ID',
      dataIndex: 'session_id',
      key: 'session_id',
      render: (text) => <Text code>{text.substring(0, 8)}...</Text>,
    },
    {
      title: 'Start Time',
      dataIndex: 'start_time',
      key: 'start_time',
      render: (text) => new Date(text).toLocaleString(),
    },
    {
      title: 'Source IP',
      dataIndex: 'src_ip',
      key: 'src_ip',
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: 'Commands',
      dataIndex: 'commands_count',
      key: 'commands_count',
    },
    {
      title: 'Duration',
      dataIndex: 'duration',
      key: 'duration',
      render: (duration) => duration ? `${duration.toFixed(2)}s` : 'Active',
    },
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '50px' }}>
        <Alert message="Error" description={error} type="error" showIcon />
      </div>
    );
  }

  const { summary, top_source_ips, top_usernames, top_passwords, top_commands, daily_attempts, recent_auth, recent_commands, recent_sessions } = dashboardData;

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        breakpoint="lg"
        collapsedWidth="0"
        onBreakpoint={(broken) => { }}
        onCollapse={(collapsed, type) => { }}
      >
        <div className="logo">
          <SecurityScanOutlined /> HADES
        </div>
        <Menu theme="dark" mode="inline" defaultSelectedKeys={['1']}>
          <Menu.Item key="1" icon={<DashboardOutlined />}>
            Dashboard
          </Menu.Item>
          <Menu.Item key="2" icon={<FileTextOutlined />}>
            Logs
          </Menu.Item>
        </Menu>
      </Sider>
      <Layout>
        <Header style={{ padding: '0 16px', background: '#fff', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <Title level={3} style={{ margin: '16px 0' }}>
            SSH Honeypot Dashboard
          </Title>
        </Header>
        <Content style={{ margin: '24px 16px 0' }}>
          <div className="site-layout-background" style={{ padding: 24, minHeight: 360 }}>

            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="Total Auth Attempts"
                    value={summary.total_auth_attempts}
                    prefix={<SecurityScanOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="Successful Logins"
                    value={summary.successful_logins}
                    prefix={<UserOutlined />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="Failed Logins"
                    value={summary.failed_logins}
                    prefix={<KeyOutlined />}
                    valueStyle={{ color: '#f5222d' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="Total Sessions"
                    value={summary.total_sessions}
                    prefix={<CodeOutlined />}
                    valueStyle={{ color: '#722ed1' }}
                  />
                </Card>
              </Col>
            </Row>

            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={12}>
                <div className="chart-container">
                  <Title level={4}>Daily Attack Trends</Title>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={daily_attempts.slice(0, 7).reverse()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="count" stroke="#8884d8" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </Col>
              <Col span={12}>
                <div className="chart-container">
                  <Title level={4}>Top Source IPs</Title>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={top_source_ips.slice(0, 5)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="src_ip" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Col>
            </Row>

            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <div className="chart-container">
                  <Title level={4}>Top Usernames</Title>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={top_usernames.slice(0, 5)}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ username, percent }) => `${username} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {top_usernames.slice(0, 5).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </Col>
              <Col span={8}>
                <div className="chart-container">
                  <Title level={4}>Top Passwords</Title>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={top_passwords.slice(0, 5)} layout="horizontal">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="password" type="category" width={80} />
                      <Tooltip />
                      <Bar dataKey="count" fill="#ffc658" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Col>
              <Col span={8}>
                <div className="chart-container">
                  <Title level={4}>Top Commands</Title>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={top_commands.slice(0, 5)}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ command, percent }) => `${command} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {top_commands.slice(0, 5).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </Col>
            </Row>

            <div className="log-table">
              <Title level={4}>Recent Activity</Title>
              <Tabs defaultActiveKey="1">
                <TabPane tab="Authentication Logs" key="1">
                  <Table
                    columns={authColumns}
                    dataSource={recent_auth}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                    scroll={{ x: true }}
                  />
                </TabPane>
                <TabPane tab="Command Logs" key="2">
                  <Table
                    columns={commandColumns}
                    dataSource={recent_commands}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                    scroll={{ x: true }}
                  />
                </TabPane>
                <TabPane tab="Sessions" key="3">
                  <Table
                    columns={sessionColumns}
                    dataSource={recent_sessions}
                    rowKey="session_id"
                    pagination={{ pageSize: 10 }}
                    scroll={{ x: true }}
                  />
                </TabPane>
              </Tabs>
            </div>

          </div>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
