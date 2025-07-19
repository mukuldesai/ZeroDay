import React from 'react';
import { Shield, Lock, Users, Database, Eye, AlertTriangle } from 'lucide-react';

const SecurityOverview: React.FC = () => {
  const securityFeatures = [
    {
      icon: <Shield className="w-8 h-8 text-blue-600" />,
      title: "Multi-Tenant Architecture",
      description: "Complete data isolation between organizations with secure tenant boundaries",
      features: ["Organization-scoped data", "User permission enforcement", "Cross-tenant protection"]
    },
    {
      icon: <Lock className="w-8 h-8 text-green-600" />,
      title: "Authentication & Authorization",
      description: "Enterprise-grade access control with role-based permissions",
      features: ["JWT-based sessions", "RBAC implementation", "Secure password hashing"]
    },
    {
      icon: <Database className="w-8 h-8 text-purple-600" />,
      title: "Data Protection",
      description: "Encrypted data storage and transmission with comprehensive backup",
      features: ["TLS 1.3 encryption", "Database isolation", "Secure vector storage"]
    },
    {
      icon: <Eye className="w-8 h-8 text-orange-600" />,
      title: "Monitoring & Auditing",
      description: "Complete audit trails and real-time security monitoring",
      features: ["Access logging", "Security events", "Compliance reporting"]
    }
  ];

  const complianceStandards = [
    { name: "SOC 2 Type II", status: "Ready" },
    { name: "ISO 27001", status: "Aligned" },
    { name: "GDPR", status: "Compliant" },
    { name: "OWASP", status: "Implemented" }
  ];

  const securityMetrics = [
    { label: "Data Encryption", value: "AES-256" },
    { label: "Session Security", value: "JWT + HTTPS" },
    { label: "Access Control", value: "Role-Based" },
    { label: "Backup Frequency", value: "Daily" }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Enterprise Security Overview
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Built with security-first principles to protect your organization's data 
          and ensure compliance with industry standards
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        {securityFeatures.map((feature, index) => (
          <div key={index} className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
            <div className="flex items-center mb-4">
              {feature.icon}
              <h3 className="text-xl font-semibold text-gray-900 ml-3">
                {feature.title}
              </h3>
            </div>
            <p className="text-gray-600 mb-4">{feature.description}</p>
            <ul className="space-y-2">
              {feature.features.map((item, idx) => (
                <li key={idx} className="flex items-center text-sm text-gray-700">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-6">
          <h3 className="text-2xl font-semibold text-gray-900 mb-6">
            Security Metrics
          </h3>
          <div className="space-y-4">
            {securityMetrics.map((metric, index) => (
              <div key={index} className="flex justify-between items-center">
                <span className="text-gray-700 font-medium">{metric.label}</span>
                <span className="bg-white px-3 py-1 rounded-full text-sm font-semibold text-blue-700">
                  {metric.value}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-emerald-100 rounded-lg p-6">
          <h3 className="text-2xl font-semibold text-gray-900 mb-6">
            Compliance Standards
          </h3>
          <div className="space-y-4">
            {complianceStandards.map((standard, index) => (
              <div key={index} className="flex justify-between items-center">
                <span className="text-gray-700 font-medium">{standard.name}</span>
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold">
                  {standard.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-amber-50 border-l-4 border-amber-400 p-6 mb-8">
        <div className="flex">
          <AlertTriangle className="w-6 h-6 text-amber-600 mr-3 mt-1" />
          <div>
            <h4 className="text-lg font-semibold text-amber-800 mb-2">
              Security Best Practices
            </h4>
            <ul className="text-amber-700 space-y-1">
              <li>• Regular security assessments and penetration testing</li>
              <li>• Automated vulnerability scanning and dependency updates</li>
              <li>• 24/7 security monitoring and incident response</li>
              <li>• Employee security training and awareness programs</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-8 border border-gray-200">
        <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
          Security Architecture
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-blue-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">User Layer</h4>
            <p className="text-sm text-gray-600">
              Authentication, authorization, and user management
            </p>
          </div>
          <div className="text-center">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-green-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Application Layer</h4>
            <p className="text-sm text-gray-600">
              API security, input validation, and business logic protection
            </p>
          </div>
          <div className="text-center">
            <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Database className="w-8 h-8 text-purple-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Data Layer</h4>
            <p className="text-sm text-gray-600">
              Encryption, backup, and secure data storage
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityOverview;