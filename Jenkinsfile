node {
    checkout scm

    def testImage = docker.build("test_hms")

    testImage.inside{


        stage("Run Mypy"){
            sh 'test/run_mypy.sh'
        }

        stage("Run Flake8"){
            sh 'test/run_flake.sh'
        }
    }

    testImage.inside('-P --network host'){
        stage("Init Database"){
            sh 'python init_db.py'
        }
    }

    testImage.withRun('-p 5000:5000 -h 0.0.0.0'){
        stage("API Test"){
            testImage.inside('-P --network host') {
                sh 'test/run_api.sh'
            }
        }
    }

     stage("Allure report"){
            allure includeProperties: false, jdk: '', results: [[path: 'test/result']]
     }

     stage("Coverage report"){
            cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'test/result/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '20, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
     }
}