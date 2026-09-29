'use client';

export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  loading = false, 
  disabled = false,
  icon: Icon,
  className = '',
  type = 'button',
  onClick,
  ...props 
}) {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all active:scale-[0.98]';
  
  const variants = {
    primary: 'bg-gradient-gold text-white hover:shadow-lg hover:shadow-brand/20 border border-transparent',
    secondary: 'bg-white/5 border border-white/10 text-white hover:bg-white/10',
    danger: 'bg-red-500/10 border border-red-500/20 text-red-500 hover:bg-red-500/20',
    ghost: 'bg-transparent text-gray-300 hover:bg-white/5 hover:text-white',
  };

  const sizes = {
    sm: 'text-sm px-3 py-1.5',
    md: 'text-sm px-4 py-2',
    lg: 'text-base px-6 py-3',
  };

  const isDisabled = disabled || loading;

  return (
    <button
      type={type}
      disabled={isDisabled}
      onClick={onClick}
      className={`
        ${baseStyles}
        ${variants[variant]}
        ${sizes[size]}
        ${isDisabled ? 'opacity-50 cursor-not-allowed active:scale-100' : ''}
        ${className}
      `}
      {...props}
    >
      {loading ? (
        <div className="w-4 h-4 mr-2 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : Icon ? (
        <Icon className="w-4 h-4 mr-2" />
      ) : null}
      {children}
    </button>
  );
}
