import unittest


class TestsVirtualEnvironment(unittest.TestCase):
    def test_01_existing_venv(self):
        """
        Verify that the VirtualEnvironment class cleans pre-existing virtual enviroments
        """
        # Arrange
        # Act
        # Assert
        pass

    def test_02_non_existing_requirements(self):
        """
        Verify that the VirtualEnvironment class reports when it can't find a requirements.txt file
        """
        # Arrange
        # Act
        # Assert
        pass

    def test_03_successful_venv_creation(self):
        """
        Verify that the VirtualEnvironment class can successfully create a virtualenv
        """
        # Arrange
        # Act
        # Assert
        pass

    def test_04_failed_venv_creation(self):
        """
        Verify that the VirtualEnvironment class raises an exception when it can't create a virtualenv
        """
        # Arrange
        # Act
        # Assert
        pass

    def test_05_install_requirements(self):
        """
        Verify that the VirtualEnvironment class install the requirements
        """
        # Arrange
        # Act
        # Assert
        pass

    def test_06_fail_install_requirements(self):
        """
        Verify that the VirtualEnvironment class raises an exception when it fails to install the requirements
        """
        # Arrange
        # Act
        # Assert
        pass

    def test_07_install_grader_requirements(self):
        """
        Verify that the VirtualEnvironment class install the requirements
        """
        # Arrange
        # Act
        # Assert
        pass

    def test_08_fail_install_grader_requirements(self):
        """
        Verify that the VirtualEnvironment class raises an exception when it fails to install the requirements
        """
        # Arrange
        # Act
        # Assert
        pass

    def test_09_teardown(self):
        """
        Verify that the VirtualEnvironment class removes the virtual environment when the context manager is exited
        """
        # Arrange
        # Act
        # Assert
        pass
