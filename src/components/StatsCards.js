'use client';

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, MessageSquare, AlertTriangle } from 'lucide-react';

export default function StatsCards({ analytics }) {
  const stats = [
    {
      title: 'Positive Mentions',
      value: analytics?.positiveMentions || 0,
      change: analytics?.positiveChange || 0,
      icon: MessageSquare,
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600',
      trendIcon: TrendingUp,
      trendColor: 'text-green-600',
      delay: 0.1
    },
    {
      title: 'Negative Mentions',
      value: analytics?.negativeMentions || 0,
      change: analytics?.negativeChange || 0,
      icon: AlertTriangle,
      iconBg: 'bg-red-100',
      iconColor: 'text-red-600',
      trendIcon: TrendingDown,
      trendColor: 'text-red-600',
      delay: 0.2
    },
    {
      title: 'Neutral Mentions',
      value: analytics?.neutralMentions || 0,
      change: null,
      icon: MessageSquare,
      iconBg: 'bg-gray-100',
      iconColor: 'text-gray-600',
      trendIcon: MessageSquare,
      trendColor: 'text-gray-600',
      delay: 0.3
    },
    {
      title: 'Reputation Score',
      value: analytics?.reputationScore || 0,
      change: analytics?.reputationTrend,
      icon: AlertTriangle,
      iconBg: analytics?.riskLevel === 'high' ? 'bg-red-100' : 
              analytics?.riskLevel === 'medium' ? 'bg-yellow-100' : 'bg-green-100',
      iconColor: analytics?.riskLevel === 'high' ? 'text-red-600' :
                 analytics?.riskLevel === 'medium' ? 'text-yellow-600' : 'text-green-600',
      trendIcon: null,
      trendColor: analytics?.reputationTrend === 'up' ? 'text-green-600' : 
                  analytics?.reputationTrend === 'down' ? 'text-red-600' : 'text-gray-600',
      delay: 0.4
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      {stats.map((stat) => {
        const Icon = stat.icon;
        const TrendIcon = stat.trendIcon;
        
        return (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: stat.delay }}
            className="bg-white border border-gray-200 rounded-lg p-6 shadow-md"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-black">{stat.value}</p>
                <div className="flex items-center mt-2">
                  {stat.change !== null && stat.change !== undefined ? (
                    <>
                      {TrendIcon && <TrendIcon className={`h-4 w-4 ${stat.trendColor} mr-1`} />}
                      <span className={`text-sm ${stat.trendColor}`}>
                        {stat.title === 'Reputation Score' ? (
                          <>
                            {analytics?.reputationTrend === 'up' ? '↗' : 
                             analytics?.reputationTrend === 'down' ? '↘' : '→'} {analytics?.reputationTrend || 'stable'}
                          </>
                        ) : (
                          `+${stat.change}%`
                        )}
                      </span>
                    </>
                  ) : (
                    <>
                      {TrendIcon && <TrendIcon className={`h-4 w-4 ${stat.trendColor} mr-1`} />}
                      <span className={`text-sm ${stat.trendColor}`}>
                        Neutral sentiment
                      </span>
                    </>
                  )}
                </div>
              </div>
              <div className={`p-3 ${stat.iconBg} rounded-full`}>
                <Icon className={`h-6 w-6 ${stat.iconColor}`} />
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
