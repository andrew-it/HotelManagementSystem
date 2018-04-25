timestamps {
    node() {
        try {
            stage ('Checkout'){
                checkout scm
            }

            stage ('Setup virtualenv') {
                sh """
                PATH=$WORKSPACE/venv/bin:/usr/local/bin:$PATH
                if [ ! -d "venv" ]; then
                        python3.6 -m virtualenv venv
                fi
                . venv/bin/activate
                which python

                python -m pip install -r requirements.txt -r test/test_requirements.txt
                """
            }

            stage ('Init DB'){
                sh """

                . venv/bin/activate
                which python

                python init_db.py

                cd data_generator
                python generateSQL.py

                """
            }

            stage ('Run Tests'){
                wrap([$class: 'Xvfb', screen: '1440x900x24']) {
                    sh """
                    . venv/bin/activate
                    which python

                    python -m nose --with-allure --logdir=./allure-results  --with-xcoverage --cover-package=app --xcoverage-file=allure-results/coverage.xml --exclude-dir=test/ui_tests ./test
                    """
                }
            }

            stage ('Run MyPy'){
                sh """
                . venv/bin/activate
                which python

                python -m mypy app --junit-xml ./allure-results/mypy.xml || true
                """
            }

            stage ('Run Flakes8') {
                sh """
                . venv/bin/activate
                which python

                cd app
                python -m flake8 --output-file ../allure-results/flake8.txt || true
                cd ..

                cd allure-results
                flake8_junit flake8.txt flake8_junit.xml
                """
            }

        } catch (e) {
            throw(e)

        } finally {
            stage ('Publish Alure Report'){
                allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
            }

            stage ('Publish Coverage Report'){
                cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'allure-results/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
            }
        }
    }
}