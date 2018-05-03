node {
    checkout scm

    def testImage

    stage("Build Docker Image"){
        testImage = docker.build("test_hms")
    }

    try {

        testImage.inside{
            stage("Unit Test"){
                sh 'test/run_unit.sh'
            }

            stage("Run Mypy"){
                sh 'test/run_mypy.sh'
            }

            stage("Run Flake8"){
                sh 'test/run_flake.sh'
            }
        }

        testImage.inside('-P --network host'){
            stage("Init Database"){
                sh """
                cd db_setup
                python db_init.py
                python db_gen.py
                """
            }
        }

        testImage.withRun('-p 5000:5000 -h 0.0.0.0 --link test_db -e HMS_DB="dbname=hms user=postgres password=postgres host=test_db"') { c ->

            try {
            stage("API Test"){
                testImage.inside('-P --network host') {
                    sh 'test/run_api.sh'
                }
            }


            stage("UI Test"){
                testImage.inside('-P --network host') {
                    sh 'test/run_ui.sh'
                }
            }


            stage("Benchmark"){
                sh """
                cd test
                ./run_bench.sh
                """
            }
            } finally {

            stage("App logs"){
                sh "docker logs ${c.id}"
            }

            }
        }

    } finally {
        stage("Allure report"){
            allure includeProperties: false, jdk: '', results: [[path: 'test/unit/result'], [path: 'test/api/result'], [path: 'test/static/result'], [path: 'test/ui/result']]
        }

        stage("Coverage report"){
            cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'test/unit/result/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '20, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
        }

        stage("Benchmark report"){
            perfReport percentiles: '0,50,90,100', sourceDataFiles: 'test/bench/result/*.wrk'
        }
    }
}