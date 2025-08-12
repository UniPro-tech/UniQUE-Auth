import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { TextInput, PasswordInput, Button, Paper, Title, Text, Container } from '@mantine/core';
import { useForm } from '@mantine/form';
import { login, getCsrfToken } from '../services/auth';

export function LoginPage() {
  const [error, setError] = useState<string | null>(null);
  const [csrfToken, setCsrfToken] = useState<string>('');
  const location = useLocation();
  const navigate = useNavigate();

  const form = useForm({
    initialValues: {
      custom_id: '',
      password: '',
    },
    validate: {
      custom_id: (value) => (value ? null : 'ユーザー名を入力してください'),
      password: (value) => (value ? null : 'パスワードを入力してください'),
    },
  });

  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        const token = await getCsrfToken();
        setCsrfToken(token);
      } catch (error) {
        setError('CSRFトークンの取得に失敗しました');
      }
    };
    fetchCsrfToken();
  }, []);

  const handleSubmit = async (values: { custom_id: string; password: string }) => {
    try {
      setError(null);
      const response = await login({
        ...values,
        csrf_token: csrfToken,
      });

      if (response.success && response.redirect_url) {
        // 認可画面またはリダイレクト先に遷移
        window.location.href = response.redirect_url;
      } else {
        setError(response.error || 'ログインに失敗しました');
      }
    } catch (error) {
      setError('ログイン処理中にエラーが発生しました');
    }
  };

  return (
    <Container size={420} my={40}>
      <Title ta="center">ログイン</Title>
      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <TextInput
            label="ユーザー名"
            placeholder="your-username"
            required
            {...form.getInputProps('custom_id')}
          />
          <PasswordInput
            label="パスワード"
            placeholder="Your password"
            required
            mt="md"
            {...form.getInputProps('password')}
          />
          {error && (
            <Text c="red" size="sm" mt="sm">
              {error}
            </Text>
          )}
          <Button type="submit" fullWidth mt="xl">
            ログイン
          </Button>
        </form>
      </Paper>
    </Container>
  );
}