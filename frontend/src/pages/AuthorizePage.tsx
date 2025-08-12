import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Container, Paper, Title, Text, Button, List, Alert } from '@mantine/core';
import { getAuthorizationData, authorize } from '../services/auth';
import type { AuthorizationData } from '../types';

export function AuthorizePage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [authData, setAuthData] = useState<AuthorizationData | null>(null);
  const location = useLocation();

  useEffect(() => {
    const fetchAuthData = async () => {
      try {
        const params = new URLSearchParams(location.search);
        const data = await getAuthorizationData({
          client_id: params.get('client_id') || '',
          redirect_uri: params.get('redirect_uri') || '',
          scope: params.get('scope') || '',
          response_type: params.get('response_type') || '',
          state: params.get('state') || undefined,
          nonce: params.get('nonce') || undefined,
        });
        setAuthData(data);
      } catch (error: any) {
        setError(error.response?.data?.error_description || error.response?.data?.error || '認可情報の取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };
    fetchAuthData();
  }, [location]);

  const handleAuthorize = async () => {
    try {
      const params = new URLSearchParams(location.search);
      const redirectUrl = await authorize({
        client_id: params.get('client_id') || '',
        redirect_uri: params.get('redirect_uri') || '',
        scope: params.get('scope') || '',
        response_type: params.get('response_type') || '',
        state: params.get('state') || undefined,
        nonce: params.get('nonce') || undefined,
      });
      window.location.href = redirectUrl;
    } catch (error: any) {
      setError(error.response?.data?.error_description || error.response?.data?.error || '認可処理中にエラーが発生しました');
    }
  };

  if (loading) {
    return (
      <Container size={420} my={40}>
        <Text>読み込み中...</Text>
      </Container>
    );
  }

  if (error) {
    return (
      <Container size={420} my={40}>
        <Alert color="red" title="エラー">
          {error}
        </Alert>
      </Container>
    );
  }

  if (!authData) {
    return (
      <Container size={420} my={40}>
        <Alert color="red" title="エラー">
          認可情報が見つかりません
        </Alert>
      </Container>
    );
  }

  return (
    <Container size={420} my={40}>
      <Title ta="center">アプリケーション認可</Title>
      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <Text size="lg" fw={500}>
          {authData.app.name}
        </Text>
        <Text size="sm" c="dimmed" mt="xs">
          このアプリケーションは以下の権限を要求しています：
        </Text>
        <List size="sm" mt="sm">
          {authData.app.scope.split(' ').map((scope) => (
            <List.Item key={scope}>{scope}</List.Item>
          ))}
        </List>
        <Text size="sm" mt="md">
          ログイン中のユーザー: {authData.user.name}
        </Text>
        <Button onClick={handleAuthorize} fullWidth mt="xl">
          認可する
        </Button>
      </Paper>
    </Container>
  );
}