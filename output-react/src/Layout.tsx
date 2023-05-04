import { Box, Button, Typography } from '@robocorp/components';
import { IconCheck2 } from '@robocorp/icons/iconic';
import { ThemeProvider } from '@robocorp/theme';

export const Layout = () => {
  return (
    <ThemeProvider name="dark">
      <Box p="$24">
        <Typography variant="display.large" mb="$12">
          Hello World
        </Typography>
        <Button icon={IconCheck2}>OB</Button>
      </Box>
    </ThemeProvider>
  );
};
