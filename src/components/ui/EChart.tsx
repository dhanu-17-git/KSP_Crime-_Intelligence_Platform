import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface EChartProps {
  option: any;
  style?: React.CSSProperties;
  className?: string;
}

export const EChart: React.FC<EChartProps> = ({ option, style, className }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Initialize ECharts instance
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    // Set configuration options
    chartInstance.current.setOption(option, true);

    const handleResize = () => {
      chartInstance.current?.resize();
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartInstance.current) {
        chartInstance.current.dispose();
        chartInstance.current = null;
      }
    };
  }, [option]);

  return (
    <div
      ref={chartRef}
      style={{ width: '100%', height: '300px', ...style }}
      className={className}
    />
  );
};
export default EChart;
