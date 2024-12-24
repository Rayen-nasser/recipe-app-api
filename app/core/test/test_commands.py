from unittest.mock import patch
from django.core.management import call_command
from django.test import TestCase
from django.db.utils import OperationalError


class CommandTests(TestCase):
    """Test custom Django commands"""

    @patch('django.db.utils.ConnectionHandler.__getitem__')
    def test_wait_for_db_ready(self, mock_getitem):
        """Test waiting for db when db is available"""
        mock_getitem.return_value = True
        call_command('wait_for_db')
        mock_getitem.assert_called_once()

    @patch('time.sleep', return_value=None)
    @patch('django.db.utils.ConnectionHandler.__getitem__')
    def test_wait_for_db_delay(self, mock_getitem, mock_sleep):
        """Test waiting for db with OperationalError"""
        mock_getitem.side_effect = [OperationalError] * 5 + [True]
        call_command('wait_for_db')
        self.assertEqual(mock_getitem.call_count, 6)
