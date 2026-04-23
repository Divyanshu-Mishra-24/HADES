import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { Typography, Card, Statistic, Row, Col, Collapse, Empty, Table } from 'antd';
import {
  GlobalOutlined,
  RadarChartOutlined,
  NodeIndexOutlined,
  UserOutlined,
  HistoryOutlined,
  FieldTimeOutlined,
  UnlockOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { Panel } = Collapse;

const NetworkMesh = ({ data, theme, compact = false, showGraph = true, showList = true }) => {
  const containerRef = useRef(null);
  const initialized = useRef(false);
  const isDark = theme === 'dark';
  const [stats, setStats] = useState({ nodes: 0, links: 0 });
  const [attackerMap, setAttackerMap] = useState({});

  useEffect(() => {
    if (!data?.recent_auth) return;

    // Grouping data by Username (IP)
    const mapping = {};

    // Create lookup maps for commands and sessions
    const commandMap = {};
    if (data.recent_commands) {
      data.recent_commands.forEach(cmd => {
        if (!commandMap[cmd.session_id]) commandMap[cmd.session_id] = [];
        commandMap[cmd.session_id].push(cmd);
      });
    }

    const sessionLookup = {};
    if (data.recent_sessions) {
      data.recent_sessions.forEach(sess => {
        sessionLookup[sess.session_id] = sess;
      });
    }

    data.recent_auth.forEach(auth => {
      const key = `${auth.username || 'ANONYMOUS'} (${auth.src_ip})`;
      if (!mapping[key]) {
        mapping[key] = {
          username: auth.username || 'ANONYMOUS',
          ip: auth.src_ip,
          attempts: []
        };
      }

      // Find associated commands and session info
      const sessionInfo = auth.session_id ? sessionLookup[auth.session_id] : null;
      const commands = auth.session_id ? (commandMap[auth.session_id] || []) : [];

      mapping[key].attempts.push({
        key: auth.id || Math.random(),
        timestamp: auth.timestamp,
        password: auth.password,
        sessionId: auth.session_id,
        service: auth.service,
        success: auth.success,
        commands: commands.map(c => c.command + (c.args ? ' ' + c.args : '')).join('\n') || '-',
        results: commands.map(c => c.result || (c.success ? 'Success' : 'Failed')).join('\n') || '-',
        startTime: sessionInfo?.start_time,
        endTime: sessionInfo?.end_time,
        observation: '' // Blank as requested
      });
    });
    setAttackerMap(mapping);
  }, [data]);

  useEffect(() => {
    if (!containerRef.current || !data || !showGraph || initialized.current) return;
    initialized.current = true;

    // Clean up previous scene if any
    while (containerRef.current.firstChild) {
      containerRef.current.removeChild(containerRef.current.firstChild);
    }

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(70, width / height, 0.1, 1000);
    camera.position.z = 50;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerRef.current.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.5;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(isDark ? 0x00ff41 : 0xff4136, 1);
    pointLight.position.set(10, 10, 10);
    scene.add(pointLight);

    // Group to hold all objects
    const group = new THREE.Group();
    scene.add(group);

    // HADES Core Node
    const coreGeometry = new THREE.SphereGeometry(3, 32, 32);
    const coreMaterial = new THREE.MeshPhongMaterial({
      color: isDark ? 0x00ff41 : 0xff4136,
      emissive: isDark ? 0x00ff41 : 0xff4136,
      emissiveIntensity: 0.5,
      transparent: true,
      opacity: 0.8,
    });
    const coreNode = new THREE.Mesh(coreGeometry, coreMaterial);
    group.add(coreNode);

    // Nodes and Links from data
    const nodes = [];
    const sourceIps = data.top_source_ips || [];

    sourceIps.forEach((ipData, index) => {
      const angle = (index / sourceIps.length) * Math.PI * 2;
      const radius = 25 + Math.random() * 10;

      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;
      const z = (Math.random() - 0.5) * 20;

      // Create IP Node
      const nodeGeom = new THREE.SphereGeometry(0.8, 16, 16);
      const nodeMat = new THREE.MeshPhongMaterial({
        color: index % 2 === 0 ? 0xbc13fe : 0x00e5ff,
        emissive: index % 2 === 0 ? 0xbc13fe : 0x00e5ff,
        emissiveIntensity: 0.4,
      });
      const node = new THREE.Mesh(nodeGeom, nodeMat);
      node.position.set(x, y, z);
      group.add(node);
      nodes.push(node);

      // Create Link (Line)
      const points = [
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(x, y, z)
      ];
      const lineGeom = new THREE.BufferGeometry().setFromPoints(points);
      const lineMat = new THREE.LineBasicMaterial({
        color: isDark ? 0x00ff41 : 0xff4136,
        transparent: true,
        opacity: 0.2,
        blending: THREE.AdditiveBlending
      });
      const line = new THREE.Line(lineGeom, lineMat);
      group.add(line);
    });

    setStats({ nodes: sourceIps.length + 1, links: sourceIps.length });

    // Animation Particles (Floating data bits)
    const particlesCount = 200;
    const particlesGeom = new THREE.BufferGeometry();
    const posArray = new Float32Array(particlesCount * 3);
    for (let i = 0; i < particlesCount * 3; i++) {
      posArray[i] = (Math.random() - 0.5) * 80;
    }
    particlesGeom.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const particlesMat = new THREE.PointsMaterial({
      size: 0.1,
      color: 0x00ff41,
      transparent: true,
      opacity: 0.5
    });
    const particles = new THREE.Points(particlesGeom, particlesMat);
    scene.add(particles);

    let frameId;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      controls.update();

      // Pulsing effect for core
      const pulse = 1 + Math.sin(Date.now() * 0.002) * 0.1;
      coreNode.scale.set(pulse, pulse, pulse);

      // Floating motion for particles
      particles.rotation.y += 0.001;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(frameId);
      if (renderer.domElement && renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
      if (renderer) {
        renderer.dispose();
        renderer.forceContextLoss();
        renderer.domElement = null;
      }
      initialized.current = false;
      // Clean up meshes
      scene.traverse(obj => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
          if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
          else obj.material.dispose();
        }
      });
    };
  }, [showGraph]);

  const formatDate = (dateStr) => {
    try {
      return new Date(dateStr).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' });
    } catch (e) {
      return dateStr;
    }
  };

  const detailColumns = [
    {
      title: 'PASSWORD',
      dataIndex: 'password',
      key: 'password',
      render: (text) => <Text code style={{ fontSize: 14, color: 'var(--text-muted)', background: 'rgba(255,255,255,0.05)', border: 'none' }}>{text}</Text>
    },
    {
      title: 'COMMANDS',
      dataIndex: 'commands',
      key: 'commands',
      render: (text) => <Text style={{ fontSize: 14, whiteSpace: 'pre-wrap', color: 'var(--text-main)', fontFamily: 'Source Code Pro' }}>{text}</Text>
    },
    {
      title: 'RESULTS',
      dataIndex: 'results',
      key: 'results',
      render: (text) => <Text style={{ fontSize: 14, whiteSpace: 'pre-wrap', color: 'var(--text-muted)', fontFamily: 'Source Code Pro' }}>{text}</Text>
    },
    {
      title: 'TIME STAMP',
      key: 'timestamp',
      render: (_, record) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Text style={{ fontSize: 11, color: 'var(--neon-accent)' }}>LOGIN: {formatDate(record.startTime || record.timestamp)}</Text>
          <Text style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            LOGOUT: {record.endTime ? formatDate(record.endTime) : <span style={{ color: '#faad14', fontWeight: 'bold' }}>CURRENTLY USING</span>}
          </Text>
        </div>
      )
    },
    {
      title: 'OBSERVATION',
      dataIndex: 'observation',
      key: 'observation',
    }
  ];

  return (
    <div className="network-mesh-container" style={{ position: 'relative', height: '100%', width: '100%' }}>
      {showGraph && (
        <div
          ref={containerRef}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            borderRadius: '16px',
            overflow: 'hidden',
            background: 'rgba(0,0,0,0.05)',
            border: '1px solid var(--glass-border)'
          }}
        />
      )}

      {/* HUD Overlays */}
      {showGraph && !compact && (
        <div style={{ position: 'absolute', top: 20, left: 20, pointerEvents: 'none' }}>
          <Title level={4} style={{ color: 'var(--neon-accent)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: 2 }}>
            <RadarChartOutlined /> Neural Network Mesh
          </Title>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div className="status-blink" style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--neon-accent)' }} />
            <Text style={{ color: 'var(--text-muted)', fontSize: 14 }}>
              REAL-TIME TOPOLOGICAL THREAT VISUALIZATION
            </Text>
          </div>
        </div>
      )}

      {/* Attacker List Panel */}
      {showList && (
        <div
          style={{
            position: showGraph ? 'absolute' : 'relative',
            top: showGraph ? (compact ? 10 : 20) : 0,
            right: showGraph ? (compact ? 10 : 20) : 0,
            width: showGraph ? (compact ? 300 : 350) : '100%',
            maxHeight: showGraph ? 'calc(100% - 100px)' : '100%',
            overflowY: 'auto',
            pointerEvents: 'auto',
            zIndex: 10,
            margin: showGraph ? 0 : '0 auto'
          }}
        >
          <div className="glass-panel" style={{ padding: '16px 0', background: 'rgba(15, 15, 20, 0.8)', border: '1px solid var(--glass-border)', boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }}>
            <div style={{ padding: '0 20px 12px 20px', borderBottom: '1px solid var(--glass-border)', marginBottom: 12 }}>
              <Title level={5} style={{ color: 'var(--text-main)', margin: 0, fontSize: 14, textTransform: 'uppercase', letterSpacing: 1.5, display: 'flex', alignItems: 'center', gap: 8 }}>
                <UserOutlined style={{ color: 'var(--neon-accent)' }} /> DETECTED INTRUDERS
              </Title>
            </div>

            <Collapse
              ghost
              accordion
              expandIconPosition="right"
              className="attacker-collapse"
              expandIcon={({ isActive }) => <HistoryOutlined style={{ color: isActive ? 'var(--neon-accent)' : 'var(--text-muted)' }} rotate={isActive ? 90 : 0} />}
            >
              {Object.keys(attackerMap).length > 0 ? (
                Object.entries(attackerMap).map(([key, info], idx) => (
                  <Panel
                    header={
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                        <Text strong style={{ color: 'var(--text-main)', fontSize: 13 }}>
                          <span style={{ color: 'var(--neon-accent)' }}>{info.username}</span> ({info.ip})
                        </Text>
                      </div>
                    }
                    key={idx}
                    style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}
                  >
                    <Table
                      className="attacker-detail-table"
                      dataSource={info.attempts}
                      columns={detailColumns}
                      pagination={false}
                      size="small"
                      scroll={{ x: 600 }}
                    />
                  </Panel>
                ))
              ) : (
                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={<span style={{ color: 'var(--text-muted)' }}>No data detected</span>} />
              )}
            </Collapse>
          </div>
        </div>
      )}

      {/* Stats Overlay */}
      {showGraph && !compact && (
        <div style={{ position: 'absolute', bottom: 20, right: 20, pointerEvents: 'none' }}>
          <Row gutter={24}>
            <Col>
              <Card className="glass-panel" style={{ padding: '8px 20px', minWidth: 140, background: 'rgba(20,20,25,0.4)', backdropFilter: 'blur(10px)' }}>
                <Statistic
                  title={<span style={{ color: 'var(--text-muted)', fontSize: 12 }}>ACTIVE NODES</span>}
                  value={stats.nodes}
                  prefix={<NodeIndexOutlined style={{ color: 'var(--neon-accent)' }} />}
                  valueStyle={{ color: 'var(--text-main)', fontSize: 24 }}
                />
              </Card>
            </Col>
            <Col>
              <Card className="glass-panel" style={{ padding: '8px 20px', minWidth: 140, background: 'rgba(20,20,25,0.4)', backdropFilter: 'blur(10px)' }}>
                <Statistic
                  title={<span style={{ color: 'var(--text-muted)', fontSize: 12 }}>SYNCED LINKS</span>}
                  value={stats.links}
                  prefix={<GlobalOutlined style={{ color: '#bc13fe' }} />}
                  valueStyle={{ color: 'var(--text-main)', fontSize: 24 }}
                />
              </Card>
            </Col>
          </Row>
        </div>
      )}

      {showGraph && !compact && (
        <div style={{ position: 'absolute', bottom: 20, left: 20, pointerEvents: 'none', maxWidth: 300 }}>
          <div className="glass-panel" style={{ padding: 16, background: 'rgba(20,20,25,0.4)' }}>
            <Text style={{ color: 'var(--text-muted)', fontSize: 14, lineHeight: 1.6 }}>
              Neural Topological Graph tracing <span style={{ color: 'var(--neon-accent)' }}>{data?.top_source_ips?.length || 0}</span> intruder endpoints.
              Central infrastructure represents HADES CORE.
              Peripheral nodes represent high-frequency attack originators detected in the current cycle.
            </Text>
          </div>
        </div>
      )}
    </div>
  );
};

export default NetworkMesh;
