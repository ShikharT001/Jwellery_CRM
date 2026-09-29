export default function Badge({ value, children }) {
  const styles = {
    active: 'bg-green-500/10 text-green-400 border-green-500/20',
    suspended: 'bg-red-500/10 text-red-400 border-red-500/20',
    trial: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    inactive: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
    invited: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  };

  const dots = {
    active: 'bg-green-400',
    suspended: 'bg-red-400',
    trial: 'bg-yellow-400',
    inactive: 'bg-gray-400',
    invited: 'bg-blue-400',
  };

  const style = styles[value.toLowerCase()] || styles.inactive;
  const dot = dots[value.toLowerCase()] || dots.inactive;

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style}`}>
      <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${dot}`} />
      {children || value}
    </span>
  );
}
