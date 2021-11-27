pipeline {
  agent any
  environment {
    ZTL_API_TOKEN = credentials('zentral-api-token')
    ZTL_FQDN = "zentral.example.com"
    ZTL_MAIN_CONFIG = "Default"
    ZTL_STAG_CONFIG = "Testing"
  }
  options {
    disableConcurrentBuilds()
  }
  stages {
    stage("Check rulesets") {
      when { anyOf { changeRequest target: 'main'; changeRequest target: 'staging' } }
      steps {
        sh '''
          if [ "$CHANGE_TARGET" = "main" ]; then
            ZTL_CONFIG=$ZTL_MAIN_CONFIG
          else
            ZTL_CONFIG=$ZTL_STAG_CONFIG
          fi
          echo "*** Check the rulesets against the $ZTL_CONFIG configuration"
          python3 scripts/post_rulesets.py rulesets "$ZTL_FQDN" "$ZTL_CONFIG" --dry-run
        '''
      }
    }
    stage("Apply rulesets") {
      when { anyOf { branch 'main'; branch 'staging' } }
      steps {
        sh '''
          if [ "$BRANCH_NAME" = "main" ]; then
            ZTL_CONFIG=$ZTL_MAIN_CONFIG
          else
            ZTL_CONFIG=$ZTL_STAG_CONFIG
          fi
          echo "*** Apply the rulesets to the $ZTL_CONFIG configuration"
          python3 scripts/post_rulesets.py rulesets "$ZTL_FQDN" "$ZTL_CONFIG"
        '''
      }
    }
  }
}
