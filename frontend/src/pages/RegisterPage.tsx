import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { authService } from '@/services';
import { Button, Input, Card, Select } from '@/components/common';
import type { RegisterData } from '@/types';
import toast from 'react-hot-toast';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterData>();

  const onSubmit = async (data: RegisterData) => {
    setIsLoading(true);
    try {
      await authService.register(data);
      toast.success('Account created! Please sign in.');
      navigate('/login');
    } catch (error: unknown) {
      const err = error as { response?: { data?: Record<string, string[]> } };
      const messages = err.response?.data;
      if (messages) {
        const first = Object.values(messages)[0];
        toast.error(Array.isArray(first) ? first[0] : 'Registration failed');
      } else {
        toast.error('Registration failed');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary-700">TIN Validation Platform</h1>
          <p className="mt-2 text-gray-600">Create your account</p>
        </div>

        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Register</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                id="first_name"
                label="First name"
                placeholder="John"
                error={errors.first_name?.message}
                {...register('first_name')}
              />
              <Input
                id="last_name"
                label="Last name"
                placeholder="Doe"
                error={errors.last_name?.message}
                {...register('last_name')}
              />
            </div>
            <Input
              id="email"
              label="Email address"
              type="email"
              placeholder="you@example.com"
              error={errors.email?.message}
              {...register('email', { required: 'Email is required' })}
            />
            <Input
              id="username"
              label="Username"
              placeholder="johndoe"
              error={errors.username?.message}
              {...register('username', { required: 'Username is required' })}
            />
            <Input
              id="organization"
              label="Organization"
              placeholder="Acme Corp"
              error={errors.organization?.message}
              {...register('organization')}
            />
            <Select
              id="role"
              label="Role"
              options={[
                { value: 'analyst', label: 'Analyst' },
                { value: 'viewer', label: 'Viewer' },
                { value: 'admin', label: 'Administrator' },
              ]}
              error={errors.role?.message}
              {...register('role')}
            />
            <Input
              id="password"
              label="Password"
              type="password"
              placeholder="Min. 8 characters"
              error={errors.password?.message}
              {...register('password', { required: 'Password is required', minLength: { value: 8, message: 'Min. 8 characters' } })}
            />
            <Input
              id="password_confirm"
              label="Confirm password"
              type="password"
              placeholder="••••••••"
              error={errors.password_confirm?.message}
              {...register('password_confirm', { required: 'Please confirm your password' })}
            />
            <Button type="submit" isLoading={isLoading} className="w-full" size="lg">
              Create account
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
};

export default RegisterPage;
